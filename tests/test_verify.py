# SPDX-License-Identifier: Apache-2.0
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from idemcore_verify.core import parse_log, check_log, compare_logs, fnv1a64, FNV_OFFSET

S = os.path.join(os.path.dirname(HERE), "samples")

class T(unittest.TestCase):
    def test_fnv_vectors(self):
        # Published FNV-1a-64 test vectors
        self.assertEqual(fnv1a64(b""), FNV_OFFSET)
        self.assertEqual(fnv1a64(b"a"), 0xaf63dc4c8601ec8c)
        self.assertEqual(fnv1a64(b"foobar"), 0x85944171f73967e8)

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
        f[2] = "%016x" % (int(f[2], 16) ^ 1)          # flip one bit of one logit hash
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

if __name__ == "__main__":
    unittest.main()


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
