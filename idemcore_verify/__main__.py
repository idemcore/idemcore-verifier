# SPDX-License-Identifier: Apache-2.0
"""Command line: python -m idemcore_verify {check,compare,check-batch,compare-batch,samples} ..."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys

from .core import (check_batch_log, check_log, compare_batch, compare_logs,
                   parse_batch_log, parse_log)
from . import __version__
from .samples import run_samples


def _print_check(path, res, as_json):
    if as_json:
        print(json.dumps({"file": path, **dataclasses.asdict(res)}))
        return
    status = "OK  " if res.ok else "FAIL"
    print(f"{status} {path}: {res.n_tokens} tokens, ALL {res.all_claimed} "
          f"(recomputed {res.all_recomputed})")
    for e in res.errors[:20]:
        print(f"     - {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="idemcore-verify",
                                 description="Check Idemcore per-token hash logs.")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="validate a log and recompute its ALL chain")
    c.add_argument("logs", nargs="+")
    c.add_argument("--json", action="store_true")
    m = sub.add_parser("compare", help="compare a candidate log against a reference log")
    m.add_argument("reference")
    m.add_argument("candidate")
    m.add_argument("--subset", action="store_true",
                   help="allow one log to cover only part of the other (spot check)")
    m.add_argument("--json", action="store_true")
    cb = sub.add_parser("check-batch", help="validate a batched (multi-stream) log and recompute every stream's ALL")
    cb.add_argument("logs", nargs="+")
    mb = sub.add_parser("compare-batch",
                        help="compare every row of a batched log against a single-stream reference log")
    mb.add_argument("reference")
    mb.add_argument("batch")
    sm = sub.add_parser("samples", help="one-command self-check: recompute every published hash in "
                        "samples/HASHES.tsv and re-check every pair in samples/PAIRS.tsv")
    sm.add_argument("--dir", default=None, help="samples directory (default: ./samples)")
    sm.add_argument("-v", "--verbose", action="store_true", help="print one line per file and pair")
    a = ap.parse_args(argv)

    if a.cmd == "samples":
        d = a.dir or ("samples" if os.path.isdir("samples") else
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples"))
        if not os.path.isfile(os.path.join(d, "HASHES.tsv")):
            print(f"idemcore-verify: no samples found at {os.path.abspath(d)}\n"
                  "The sample logs are not part of the pip package. Run this command inside a\n"
                  "clone of https://github.com/idemcore/idemcore-verifier or the unzipped release\n"
                  "archive, or pass --dir PATH/TO/samples.", file=sys.stderr)
            return 2
        return run_samples(d, verbose=a.verbose)

    if a.cmd == "check-batch":
        ok = True
        for p in a.logs:
            r = check_batch_log(parse_batch_log(p))
            print(f"{'OK  ' if r.ok else 'FAIL'} {p}: {r.n_streams} streams, {r.n_rows} rows "
                  f"({r.n_filler_rows} filler), ALL[0] {r.all_by_stream.get(0)}, STREAMS {r.streams_digest}")
            for e in r.errors[:20]:
                print(f"     - {e}")
            ok &= r.ok
        return 0 if ok else 1

    if a.cmd == "compare-batch":
        ref, b = parse_log(a.reference), parse_batch_log(a.batch)
        rr, rb = check_log(ref), check_batch_log(b)
        res = compare_batch(ref, b)
        ok = rr.ok and rb.ok and res.ok
        _print_check(a.reference, rr, False)
        print(f"{'OK  ' if rb.ok else 'FAIL'} {a.batch}: {rb.n_streams} streams, {rb.n_rows} rows")
        for e in rb.errors[:20]:
            print(f"     - {e}")
        print(f"{'MATCH' if ok else 'DIVERGE'}: {res.matched}/{res.compared} batched rows identical to the "
              f"reference (missing in reference {res.missing_in_ref})")
        if res.first_divergence:
            print(f"  first divergence: {res.first_divergence}")
        return 0 if ok else 1

    if a.cmd == "check":
        ok = True
        for p in a.logs:
            r = check_log(parse_log(p))
            _print_check(p, r, a.json)
            ok &= r.ok
        return 0 if ok else 1

    ref, cand = parse_log(a.reference), parse_log(a.candidate)
    rr, rc = check_log(ref), check_log(cand)
    res = compare_logs(ref, cand, subset=a.subset)
    ok = rr.ok and rc.ok and res.ok
    if a.json:
        print(json.dumps({"ok": ok, "reference": dataclasses.asdict(rr),
                          "candidate": dataclasses.asdict(rc),
                          "compare": dataclasses.asdict(res)}))
    else:
        _print_check(a.reference, rr, False)
        _print_check(a.candidate, rc, False)
        print(f"{'MATCH' if ok else 'DIVERGE'}: {res.matched}/{res.compared} positions identical "
              f"(mode {res.mode}; only-in-ref {res.only_in_ref}, only-in-cand {res.only_in_cand})")
        if res.first_divergence:
            d = res.first_divergence
            print(f"  first divergence at payload {d['pi']} position {d['j']}: fields {d['fields']}")
            print(f"    ref  (line {d['ref_line']}): {d['ref']}")
            print(f"    cand (line {d['cand_line']}): {d['cand']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
