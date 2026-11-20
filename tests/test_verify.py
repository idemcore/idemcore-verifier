# SPDX-License-Identifier: Apache-2.0
import gzip, hashlib, io, os, subprocess, sys, tempfile, unittest
from contextlib import redirect_stdout
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from idemcore_verify import __version__
from idemcore_verify.core import (EMPTY_DIGEST, V2_TAG, chain_v2, check_batch_log, check_log, compare_batch,
                                  compare_logs, format_v2_log, parse_batch_log, parse_log, step_digest, streams_digest)
from idemcore_verify.__main__ import main

EX = os.path.join(HERE, "vectors", "v2_example.log")
S = os.path.join(ROOT, "samples")
H = lambda s: hashlib.sha256(s.encode()).hexdigest()


def rows(n, salt=""):
    return [(i // 4, i % 4, H(f"h{i}{salt}"), H(f"c{i}")) for i in range(n)]


def lines_of(text):
    return text.splitlines()


class Format(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.4.0")

    def test_empty_digest(self):
        self.assertEqual(EMPTY_DIGEST, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(step_digest(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_example_vector(self):
        r = check_log(parse_log(EX))
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.n_positions, 8)
        self.assertEqual(r.chain_recomputed, "f4ce37fdf9cbcb300331d0c8e04cca6586276e0365156d009f6d89ef342c8a6c")

    def test_chain_matches_shell_recipe(self):
        # (printf 'idemcore-log/v2\n'; grep -E '^[0-9]' run.log) | sha256sum
        with open(EX) as f:
            body = "".join(l for l in f if l[:1].isdigit())
        self.assertEqual(hashlib.sha256((V2_TAG + "\n" + body).encode()).hexdigest(), check_log(parse_log(EX)).chain_claimed)

    def test_writer_roundtrip(self):
        t = format_v2_log(rows(10), comments=["test"])
        r = check_log(parse_log("x", lines_of(t)))
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.n_positions, 10)

    def test_writer_rejects_short_digest(self):
        with self.assertRaises(ValueError):
            format_v2_log([(0, 0, "ab", EMPTY_DIGEST)])


class Strictness(unittest.TestCase):
    def setUp(self):
        self.good = lines_of(format_v2_log(rows(8)))

    def bad(self, lines):
        return check_log(parse_log("x", lines))

    def test_tamper_one_digit(self):
        L = list(self.good)
        f = L[3].split(); f[2] = ("0" if f[2][0] != "0" else "1") + f[2][1:]
        L[3] = " ".join(f)
        r = self.bad(L)
        self.assertFalse(r.ok)
        self.assertTrue(any("CHAIN mismatch" in e for e in r.errors))
        res = compare_logs(parse_log("a", self.good), parse_log("b", L))
        self.assertFalse(res.ok)
        self.assertEqual((res.first_divergence["pi"], res.first_divergence["j"]), (0, 2))

    def test_uppercase_rejected(self):
        L = list(self.good); L[2] = L[2].upper()
        self.assertFalse(self.bad(L).ok)

    def test_leading_zero_rejected(self):
        L = list(self.good); L[2] = "0" + L[2]
        self.assertFalse(self.bad(L).ok)

    def test_double_space_rejected(self):
        L = list(self.good); L[2] = L[2].replace(" ", "  ", 1)
        self.assertFalse(self.bad(L).ok)

    def test_duplicate_position_rejected(self):
        L = self.good[:3] + [self.good[2]] + self.good[3:]
        self.assertTrue(any("duplicate" in e for e in self.bad(L).errors))

    def test_missing_chain(self):
        self.assertTrue(any("no CHAIN" in e for e in self.bad(self.good[:-1]).errors))

    def test_all_or_seal_line_rejected(self):
        for kw in ("ALL 0123456789abcdef", "SEAL " + EMPTY_DIGEST):
            self.assertFalse(self.bad(self.good[:-1] + [kw] + self.good[-1:]).ok)

    def test_reserved_keyword_ignored_and_comments(self):
        L = ["# comment"] + self.good[:2] + ["NOTE anything"] + self.good[2:]
        self.assertTrue(self.bad(L).ok)

    def test_crlf_rejected(self):
        L = [l + "\r" for l in self.good]
        self.assertFalse(self.bad(L).ok)

    def test_earlier_format_reported_as_legacy(self):
        legacy = ["0 0 0123456789abcdef 0123456789abcdef", "ALL 0123456789abcdef"]
        r = self.bad(legacy)
        self.assertFalse(r.ok)
        self.assertEqual(r.format, "legacy")
        res = compare_logs(parse_log("a", legacy), parse_log("b", self.good))
        self.assertFalse(res.ok)
        self.assertIn("earlier format", res.error)

    def test_gzip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.log.gz")
            with gzip.open(p, "wt") as f:
                f.write("\n".join(self.good) + "\n")
            self.assertTrue(check_log(parse_log(p)).ok)


class Compare(unittest.TestCase):
    def test_exact_and_subset(self):
        full = parse_log("full", lines_of(format_v2_log(rows(16))))
        part = parse_log("part", lines_of(format_v2_log(rows(16)[:6])))
        self.assertTrue(compare_logs(full, full).ok)
        self.assertFalse(compare_logs(full, part).ok)
        r = compare_logs(full, part, subset=True)
        self.assertTrue(r.ok); self.assertEqual(r.compared, 6)

    def test_order_matters_for_exact(self):
        R = rows(8)
        a = parse_log("a", lines_of(format_v2_log(R)))
        b = parse_log("b", lines_of(format_v2_log(R[1:] + R[:1])))
        self.assertFalse(compare_logs(a, b).ok)
        self.assertTrue(compare_logs(a, b, subset=True).ok)

    def test_hc_difference_detected(self):
        R = rows(8); R2 = list(R); R2[5] = (R[5][0], R[5][1], R[5][2], EMPTY_DIGEST)
        r = compare_logs(parse_log("a", lines_of(format_v2_log(R))), parse_log("b", lines_of(format_v2_log(R2))))
        self.assertFalse(r.ok); self.assertEqual(r.first_divergence["fields"], ["hc"])


class Batch(unittest.TestCase):
    def make(self, streams, filler=()):
        out = [f"FORMAT {V2_TAG}"]
        chains = {}
        for s, R in streams.items():
            body = [f"{pi} {j} {h} {hc}\n" for pi, j, h, hc in R]
            out += [f"{s} {l.strip()}" for l in body]
            chains[s] = chain_v2(body)
        for s, R in filler:
            out += [f"{s} {pi} {j} {h} {hc}" for pi, j, h, hc in R]
        out += [f"CHAIN {s} {c}" for s, c in chains.items()]
        return out, chains

    def test_batch_check_and_compare(self):
        R = rows(12)
        L, chains = self.make({0: R[:6], 1: R[6:]}, filler=[(1000, R[:2])])
        b = parse_batch_log("b", L)
        r = check_batch_log(b)
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.n_filler_rows, 2)
        self.assertEqual(r.streams_digest, streams_digest(chains))
        ref = parse_log("r", lines_of(format_v2_log(R)))
        self.assertTrue(compare_batch(ref, b).ok)

    def test_batch_tamper(self):
        R = rows(12)
        L, _ = self.make({0: R[:6], 1: R[6:]})
        L[3] = L[3][:-1] + ("0" if L[3][-1] != "0" else "1")
        self.assertFalse(check_batch_log(parse_batch_log("b", L)).ok)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(list(args))
        return rc, buf.getvalue()

    def test_check_ok(self):
        rc, out = self.run_cli("check", EX)
        self.assertEqual(rc, 0); self.assertIn("format v2, 8 positions", out)

    def test_legacy_file_fails_clearly(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "old.log")
            open(p, "w").write("0 0 0123456789abcdef 0123456789abcdef\nALL 0123456789abcdef\n")
            rc, out = self.run_cli("check", p)
            self.assertEqual(rc, 1); self.assertIn("earlier format", out)

    def test_samples_self_check(self):
        if not os.path.isfile(os.path.join(S, "HASHES.tsv")):
            self.skipTest("no samples directory")
        rc, out = self.run_cli("samples", "--dir", S)
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
