# SPDX-License-Identifier: Apache-2.0
"""One-command self-check of the published evidence.

1. For every row of samples/HASHES.tsv, recompute the log's digest(s) from its
   per-token lines and compare with the published value.
2. For every row of samples/PAIRS.tsv, compare candidate against reference
   (modes: exact, subset, batch).
Prints PASS or FAIL and returns 0 / 1.
"""
from __future__ import annotations

import os
from typing import List

from .core import (check_batch_log, check_log, compare_batch, compare_logs,
                   parse_batch_log, parse_log)


def _rows(path: str) -> List[List[str]]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            out.append(line.split("\t"))
    return out


def run_samples(d: str, verbose: bool = False) -> int:
    failures: List[str] = []
    n_files = n_pairs = n_rows = 0
    cache = {}

    def single(rel):
        if rel not in cache:
            cache[rel] = parse_log(os.path.join(d, rel))
        return cache[rel]

    print(f"idemcore-verify self-check of {os.path.abspath(d)}")
    print("[1/2] recompute published hashes (HASHES.tsv)")
    for r in _rows(os.path.join(d, "HASHES.tsv")):
        rel, kind, exp_all, exp_streams = r[0], r[1], r[8], r[9]
        n_files += 1
        try:
            if kind == "single":
                c = check_log(single(rel))
                got, got_s = c.all_recomputed, "-"
                ok = c.ok and got == exp_all
                n_rows += c.n_tokens
            else:
                c = check_batch_log(parse_batch_log(os.path.join(d, rel)))
                got, got_s = c.all_by_stream.get(0, "-"), c.streams_digest
                ok = c.ok and got == exp_all and got_s == exp_streams
                n_rows += c.n_rows
        except OSError as e:
            ok, got, got_s = False, f"unreadable ({e})", "-"
        if not ok:
            failures.append(f"hash  {rel}: published {exp_all}/{exp_streams}, recomputed {got}/{got_s}")
        if verbose or not ok:
            print(f"  {'PASS' if ok else 'FAIL'} {rel}  ALL {got}" + ("" if got_s == "-" else f"  STREAMS {got_s}"))

    print("[2/2] re-check reference/candidate pairs (PAIRS.tsv)")
    for r in _rows(os.path.join(d, "PAIRS.tsv")):
        ref, cand, mode, what = r[0], r[1], r[2], r[3] if len(r) > 3 else ""
        n_pairs += 1
        try:
            if mode == "batch":
                b = parse_batch_log(os.path.join(d, cand))
                res = compare_batch(single(ref), b)
                ok = res.ok and check_batch_log(b).ok and check_log(single(ref)).ok
                detail = f"{res.matched}/{res.compared} rows"
            else:
                rl, cl = single(ref), single(cand)
                res = compare_logs(rl, cl, subset=(mode == "subset"))
                ok = res.ok and check_log(rl).ok and check_log(cl).ok
                detail = f"{res.matched}/{res.compared} positions"
        except OSError as e:
            ok, detail = False, f"unreadable ({e})"
        if not ok:
            failures.append(f"pair  {what}: {detail}")
        if verbose or not ok:
            print(f"  {'PASS' if ok else 'FAIL'} {what}  ({detail})")

    print(f"checked {n_files} logs ({n_rows} token rows) and {n_pairs} pairs")
    if failures:
        print(f"FAIL: {len(failures)} problem(s)")
        for f in failures:
            print("  - " + f)
        return 1
    print("PASS: every published hash recomputes and every pair is bit-identical")
    return 0
