# SPDX-License-Identifier: Apache-2.0
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from idemcore_verify.core import parse_log, check_log, compare_logs, legacy_checksum64, LEGACY_BASIS

S = os.path.join(os.path.dirname(HERE), "samples")

class T(unittest.TestCase):
    def test_legacy_checksum_vectors(self):
        # Test vectors of the frozen format v1 checksum
        self.assertEqual(legacy_checksum64(b""), LEGACY_BASIS)
        self.assertEqual(legacy_checksum64(b"a"), 0xaf63dc4c8601ec8c)
        self.assertEqual(legacy_checksum64(b"foobar"), 0x85944171f73967e8)

    def test_old_import_names_still_work(self):
        # Code written against 0.3.6 imports these names; they must keep working.
        import idemcore_verify.core as core
        self.assertIs(getattr(core, "fnv1a64"), legacy_checksum64)
        self.assertEqual(getattr(core, "FNV_OFFSET"), LEGACY_BASIS)
        self.assertEqual(getattr(core, "fnv1a64_u64")(1, LEGACY_BASIS),
                         core.legacy_checksum64_word(1, LEGACY_BASIS))
        with self.assertRaises(AttributeError):
            getattr(core, "no_such_name")

    def test_samples_chain(self):
        n = 0
        for root, _dirs, files in os.walk(S):
            if os.sep + "batched" in root:
                continue
            for f in files:
                if f.endswith(".log"):
                    r = check_log(parse_log(os.path.join(root, f)))
                    self.assertTrue(r.ok, (f, r.errors))
                    n += 1
        self.assertGreater(n, 20)

    def test_tamper_detected(self):
        p = os.path.join(S, "qwen2.5-7b-int4-g", "x86_64.log")
        with open(p) as fh:
            lines = fh.read().splitlines()
        f = lines[100].split()
        f[2] = "%016x" % (int(f[2], 16) ^ 1)          # flip one bit of one h value
        bad = lines[:100] + [" ".join(f)] + lines[101:]
        log = parse_log("tampered", bad)
        self.assertFalse(check_log(log).ok)           # chain no longer matches ALL
        ref = parse_log(p)
        res = compare_logs(ref, log)
        self.assertFalse(res.ok)
        self.assertEqual((res.first_divergence["pi"], res.first_divergence["j"]),
                         (ref.tokens[100].pi, ref.tokens[100].j))

    def test_public_four_field_log(self):
        # The hosted API serves `pi j h hc` lines (idemcore-log/r1-public).
        p = os.path.join(S, "qwen2.5-7b-int4-g", "x86_64.log")
        with open(p) as fh:
            lines = fh.read().splitlines()
        pub = [" ".join(l.split()[:4]) if l[:1].isdigit() else l for l in lines]
        log = parse_log("public", pub)
        r = check_log(log)
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.all_recomputed, check_log(parse_log(p)).all_recomputed)
        self.assertTrue(compare_logs(parse_log(p), log).ok)
        f = pub[100].split()
        f[3] = "%016x" % (int(f[3], 16) ^ 1)
        bad = pub[:100] + [" ".join(f)] + pub[101:]
        self.assertFalse(check_log(parse_log("bad", bad)).ok)
        self.assertFalse(compare_logs(parse_log(p), parse_log("bad", bad)).ok)
        five = pub[:100] + [pub[100] + " 7"] + pub[101:]
        self.assertFalse(check_log(parse_log("five", five)).ok)

    def test_legacy_six_field_log(self):
        # Logs written before 0.3.2 carry two optional legacy fields per line;
        # they are checked and compared verbatim but are not part of ALL.
        p = os.path.join(S, "qwen2.5-7b-int4-g", "x86_64.log")
        with open(p) as fh:
            lines = fh.read().splitlines()
        six = [l + " 3 7" if l[:1].isdigit() else l for l in lines]
        log6 = parse_log("six", six)
        r = check_log(log6)
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.all_recomputed, check_log(parse_log(p)).all_recomputed)
        self.assertTrue(compare_logs(parse_log(p), log6).ok)      # hash-only vs 6-field
        other = [l + " 4 7" if l[:1].isdigit() else l for l in lines]
        self.assertFalse(compare_logs(log6, parse_log("other", other)).ok)
        bad = six[:100] + [" ".join(six[100].split()[:4] + ["0", "7"])] + six[101:]
        self.assertFalse(check_log(parse_log("bad", bad)).ok)    # malformed legacy field


class BatchTests(unittest.TestCase):
    B = os.path.join(S, "batched", "qwen2.5-7b-int4-g", "nvidia_a10g", "w512_b8.log.gz")
    REF = os.path.join(S, "qwen2.5-7b-int4-g", "x86_64.log")

    def test_batch_log_checks_and_matches(self):
        from idemcore_verify.core import check_batch_log, compare_batch, parse_batch_log
        b = parse_batch_log(self.B)
        c = check_batch_log(b)
        self.assertTrue(c.ok, c.errors)
        self.assertEqual(c.n_streams, 8)
        self.assertEqual(c.all_by_stream[0], "a921e042378ae5a7")
        r = compare_batch(parse_log(self.REF), b)
        self.assertTrue(r.ok)
        self.assertEqual(r.matched, c.n_rows)

    def test_batch_tamper_detected(self):
        import gzip, tempfile
        from idemcore_verify.core import check_batch_log, compare_batch, parse_batch_log
        with gzip.open(self.B, "rt") as g:
            lines = g.read().splitlines()
        f = lines[100].split()
        f[3] = format(int(f[3], 16) ^ 1, "016x")
        lines[100] = " ".join(f)
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as t:
            t.write("\n".join(lines) + "\n")
        try:
            b = parse_batch_log(t.name)
            self.assertFalse(check_batch_log(b).ok)
            self.assertFalse(compare_batch(parse_log(self.REF), b).ok)
        finally:
            os.unlink(t.name)

    def test_batch_hash_only_and_legacy(self):
        from idemcore_verify.core import check_batch_log, compare_batch, parse_batch_log, read_lines
        lines = read_lines(self.B)
        five = parse_batch_log("five", lines)
        self.assertTrue(all(t.freq is None for _, t in five.rows))
        seven = [l + " 3 7" if l[:1].isdigit() else l for l in lines]
        b7 = parse_batch_log("seven", seven)
        c5, c7 = check_batch_log(five), check_batch_log(b7)
        self.assertTrue(c7.ok, c7.errors)
        self.assertEqual(c5.streams_digest, c7.streams_digest)
        self.assertTrue(compare_batch(parse_log(self.REF), b7).ok)
        six = [l + " 3" if l[:1].isdigit() else l for l in lines[:50]] + lines[50:]
        self.assertFalse(check_batch_log(parse_batch_log("six", six)).ok)

    def test_self_check_passes(self):
        import contextlib, io
        from idemcore_verify.samples import run_samples
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_samples(S)
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("PASS", buf.getvalue())


class V2Tests(unittest.TestCase):
    """Format v2 (idemcore-log/v2): SHA-256 per-position digests and chain."""
    EX = os.path.join(HERE, "vectors", "v2_example.log")
    V1REF = os.path.join(S, "qwen2.5-7b-int4-g", "x86_64.log")

    def lines(self):
        with open(self.EX) as fh:
            return fh.read().splitlines()

    def test_example_checks(self):
        r = check_log(parse_log(self.EX))
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.format, "v2")
        self.assertEqual(r.n_tokens, 8)
        self.assertEqual(r.all_recomputed,
                         "f4ce37fdf9cbcb300331d0c8e04cca6586276e0365156d009f6d89ef342c8a6c")

    def test_chain_is_plain_sha256_of_tag_and_lines(self):
        # Independent recomputation with hashlib only (no verifier code).
        import hashlib
        body = "".join(l + "\n" for l in self.lines() if l[:1].isdigit())
        want = hashlib.sha256(("idemcore-log/v2\n" + body).encode()).hexdigest()
        claimed = [l.split()[1] for l in self.lines() if l.startswith("CHAIN ")][0]
        self.assertEqual(want, claimed)

    def test_writer_round_trip(self):
        from idemcore_verify.core import format_v2_log, step_digest, EMPTY_DIGEST
        rows = [(0, j, step_digest(bytes([j])), EMPTY_DIGEST) for j in range(5)]
        txt = format_v2_log(rows)
        log = parse_log("w", txt.splitlines())
        self.assertTrue(check_log(log).ok)
        self.assertTrue(compare_logs(log, parse_log("w2", txt.splitlines())).ok)
        with self.assertRaises(ValueError):
            format_v2_log([(0, 0, "ab", EMPTY_DIGEST)])

    def test_tamper_detected(self):
        L = self.lines()
        i = next(k for k, l in enumerate(L) if l.startswith("1 2 "))
        f = L[i].split()
        f[2] = format(int(f[2], 16) ^ 1, "064x")
        bad = L[:i] + [" ".join(f)] + L[i + 1:]
        self.assertFalse(check_log(parse_log("bad", bad)).ok)
        res = compare_logs(parse_log(self.EX), parse_log("bad", bad))
        self.assertFalse(res.ok)
        self.assertEqual((res.first_divergence["pi"], res.first_divergence["j"]), (1, 2))
        self.assertEqual(len(res.first_divergence["ref"]["h"]), 64)

    def test_positions_are_bound(self):
        # Unlike format v1, the v2 chain covers (pi, j): renumbering breaks it.
        L = self.lines()
        i = next(k for k, l in enumerate(L) if l.startswith("1 3 "))
        bad = L[:i] + ["1 9 " + L[i][4:]] + L[i + 1:]
        self.assertFalse(check_log(parse_log("renum", bad)).ok)

    def test_strict_form(self):
        L = self.lines()
        i = next(k for k, l in enumerate(L) if l[:1].isdigit())
        for mutate in (lambda l: l.upper().replace("FORMAT", "FORMAT"),   # upper-case hex
                       lambda l: l.replace(" ", "  ", 1),                 # double space
                       lambda l: "0" + l,                                 # leading zero
                       lambda l: l + " 3 7",                              # legacy fields
                       lambda l: " ".join(l.split()[:2] + [l.split()[2][:16], l.split()[3][:16]])):
            bad = L[:i] + [mutate(L[i])] + L[i + 1:]
            self.assertFalse(check_log(parse_log("bad", bad)).ok, mutate(L[i]))
        nofmt = [l for l in L if not l.startswith("FORMAT")]
        self.assertFalse(check_log(parse_log("nofmt", nofmt)).ok)
        noall = [l.replace("CHAIN", "ALL") for l in L]
        self.assertFalse(check_log(parse_log("noall", noall)).ok)
        other = [l.replace("idemcore-log/v2", "idemcore-log/v9") for l in L]
        self.assertFalse(check_log(parse_log("other", other)).ok)
        two = L + [l for l in L if l.startswith("CHAIN")]
        self.assertFalse(check_log(parse_log("two", two)).ok)

    def test_cross_format_compare_refused(self):
        res = compare_logs(parse_log(self.V1REF), parse_log(self.EX))
        self.assertFalse(res.ok)
        self.assertIn("different formats", res.error)

    def test_batch_v2(self):
        from idemcore_verify.core import (check_batch_log, compare_batch, parse_batch_log,
                                          chain_v2, streams_digest)
        body = [l for l in self.lines() if l[:1].isdigit()]
        rows = ["0 " + l for l in body] + ["1 " + l for l in body[:4]] + ["1000 " + body[5]]
        c0 = chain_v2(l + "\n" for l in body)
        c1 = chain_v2(l + "\n" for l in body[:4])
        txt = ["FORMAT idemcore-log/v2"] + rows + [f"CHAIN 0 {c0}", f"CHAIN 1 {c1}"]
        b = parse_batch_log("b", txt)
        r = check_batch_log(b)
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.n_streams, 2)
        self.assertEqual(r.n_filler_rows, 1)
        self.assertEqual(r.streams_digest, streams_digest({0: c0, 1: c1}, "v2"))
        self.assertTrue(compare_batch(parse_log(self.EX), b).ok)
        bad = list(txt)
        bad[3] = bad[3][:-1] + ("0" if bad[3][-1] != "0" else "1")
        self.assertFalse(check_batch_log(parse_batch_log("bad", bad)).ok)
        self.assertFalse(compare_batch(parse_log(self.V1REF), b).ok)   # format mismatch


class SealTests(unittest.TestCase):
    """Optional SHA-256 SEAL line on a legacy format v1 log."""
    P = os.path.join(S, "qwen2.5-0.5b-int8", "x86_64_sub240.log")

    def test_seal_round_trip_and_tamper(self):
        import hashlib
        base = parse_log(self.P)
        seal = base.seal()
        with open(self.P) as fh:
            L = fh.read().splitlines()
        body = "".join(" ".join(l.split()[:4]) + "\n" for l in L if l[:1].isdigit())
        self.assertEqual(seal, hashlib.sha256(("idemcore-log/v1-seal\n" + body).encode()).hexdigest())
        sealed = L + [f"SEAL {seal}"]
        r = check_log(parse_log("sealed", sealed))
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.all_recomputed, check_log(base).all_recomputed)   # ALL unchanged
        self.assertTrue(compare_logs(base, parse_log("sealed", sealed)).ok)
        self.assertFalse(check_log(parse_log("badseal", L + ["SEAL " + "0" * 64])).ok)

    def test_cli_seal_and_check(self):
        import contextlib, io, tempfile
        from idemcore_verify.__main__ import main
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "sealed.log")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(main(["seal", self.P, "-o", out]), 0)
                self.assertEqual(main(["check", out]), 0)
                self.assertEqual(main(["compare", self.P, out]), 0)
                self.assertEqual(main(["check", V2Tests.EX]), 0)
            self.assertIn("SEAL ok", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
