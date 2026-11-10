# SPDX-License-Identifier: Apache-2.0
"""Parsing and checking of Idemcore per-token hash logs (log format v1).

A log is a text file with one line per generated/scored token:

    <pi> <j> <h> <hc> <freq> <total>

  pi     payload (sequence) index, decimal
  j      token position inside the payload, decimal
  h      64-bit hash of the engine's output (logits) at this position, 16 hex
  hc     second 64-bit hash, of the engine's token-choice output, 16 hex
  freq   optional legacy field (logs written before 0.3.2), decimal
  total  optional legacy field (logs written before 0.3.2), decimal
         (checked for well-formedness and compared verbatim; not part of ALL)

The *hash-only* (public) form of the same log (``idemcore-log/r1-public``,
served by the hosted API and used for the published sample logs) carries the
first four fields only,

    <pi> <j> <h> <hc>

This verifier accepts both forms. ``ALL`` depends only on ``h`` and ``hc``, so
it is the same for the full and the hash-only form of a run.

followed by a chain line

    ALL <16 hex>

where ALL = fold over all token lines, in file order, of
    a = fnv1a64(le64(h), a); a = fnv1a64(le64(hc), a)
starting from the FNV-1a-64 offset basis.  Other lines that start with a
keyword (not a number) are reserved for future versions and ignored.
"""
from __future__ import annotations

import dataclasses
import gzip
from typing import Dict, Iterable, List, Optional, Tuple

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK64 = (1 << 64) - 1


def fnv1a64(data: bytes, h: int = FNV_OFFSET) -> int:
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return h


def fnv1a64_u64(v: int, h: int) -> int:
    """FNV-1a-64 over the 8 little-endian bytes of v (no allocation)."""
    for i in range(8):
        h ^= (v >> (8 * i)) & 0xFF
        h = (h * FNV_PRIME) & MASK64
    return h


@dataclasses.dataclass(frozen=True)
class TokenLine:
    pi: int
    j: int
    h: int
    hc: int
    freq: Optional[int]   # None in a public (4-field) log line
    total: Optional[int]
    lineno: int

    @property
    def key(self) -> Tuple[int, int]:
        return (self.pi, self.j)


@dataclasses.dataclass
class Log:
    path: str
    tokens: List[TokenLine]
    all_hex: Optional[str]
    errors: List[str]

    def chain(self) -> int:
        a = FNV_OFFSET
        for t in self.tokens:
            a = fnv1a64_u64(t.h, a)
            a = fnv1a64_u64(t.hc, a)
        return a

    def by_key(self) -> Dict[Tuple[int, int], TokenLine]:
        return {t.key: t for t in self.tokens}


def read_lines(path: str) -> List[str]:
    """Read a log as ASCII lines; files ending in .gz are read with gzip."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="ascii") as f:
        return f.read().splitlines()


def parse_log(path: str, lines: Optional[Iterable[str]] = None) -> Log:
    if lines is None:
        lines = read_lines(path)
    toks: List[TokenLine] = []
    errors: List[str] = []
    all_hex = None
    seen = set()
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "ALL":
            if len(p) != 2 or len(p[1]) != 16:
                errors.append(f"line {n}: malformed ALL line")
            all_hex = p[1].lower()
            continue
        if not p[0].isdigit():
            continue  # reserved keyword line (format v1 ignores it)
        if len(p) not in (4, 6):
            errors.append(f"line {n}: expected 6 fields (or 4 in a hash-only log), got {len(p)}")
            continue
        try:
            pi, j = int(p[0]), int(p[1])
            if len(p[2]) != 16 or len(p[3]) != 16:
                raise ValueError("hash field is not 16 hex digits")
            h, hc = int(p[2], 16), int(p[3], 16)
            freq = total = None
            if len(p) == 6:
                freq, total = int(p[4]), int(p[5])
        except ValueError as e:
            errors.append(f"line {n}: {e}")
            continue
        if total is not None and not (total > 0):
            errors.append(f"line {n}: legacy field total {total} out of range")
        if freq is not None and total is not None and not (0 < freq <= total):
            errors.append(f"line {n}: freq {freq} not in (0, total]")
        if (pi, j) in seen:
            errors.append(f"line {n}: duplicate position ({pi},{j})")
        seen.add((pi, j))
        toks.append(TokenLine(pi, j, h, hc, freq, total, n))
    if all_hex is None:
        errors.append("no ALL line")
    return Log(path, toks, all_hex, errors)


@dataclasses.dataclass
class CheckResult:
    ok: bool
    n_tokens: int
    all_claimed: Optional[str]
    all_recomputed: str
    errors: List[str]


def check_log(log: Log) -> CheckResult:
    rec = "%016x" % log.chain()
    errs = list(log.errors)
    if log.all_hex is not None and rec != log.all_hex:
        errs.append(f"ALL mismatch: file says {log.all_hex}, recomputed {rec}")
    return CheckResult(not errs, len(log.tokens), log.all_hex, rec, errs)


@dataclasses.dataclass
class CompareResult:
    ok: bool
    compared: int
    matched: int
    only_in_ref: int
    only_in_cand: int
    first_divergence: Optional[dict]
    mode: str


def _diff_fields(r: TokenLine, c: TokenLine) -> List[str]:
    """Fields that differ. freq/total are compared only when both lines carry
    them (a public 4-field log line has neither)."""
    out = [f for f in ("h", "hc") if getattr(r, f) != getattr(c, f)]
    if r.freq is not None and c.freq is not None:
        out += [f for f in ("freq", "total") if getattr(r, f) != getattr(c, f)]
    return out


def compare_logs(ref: Log, cand: Log, subset: bool = False) -> CompareResult:
    """Compare candidate against reference position by position.

    subset=False: both logs must cover exactly the same positions.
    subset=True : every position in the *smaller* log must appear, identical,
                  in the larger one (e.g. a CPU spot-check of a GPU run).
    """
    R, C = ref.by_key(), cand.by_key()
    keys = sorted(set(R) & set(C))
    matched = 0
    first = None
    for k in keys:
        r, c = R[k], C[k]
        diff = _diff_fields(r, c)
        if not diff:
            matched += 1
        elif first is None:
            first = {
                "pi": k[0], "j": k[1], "fields": diff,
                "ref": {f: (("%016x" % getattr(r, f)) if f in ("h", "hc") else getattr(r, f)) for f in diff},
                "cand": {f: (("%016x" % getattr(c, f)) if f in ("h", "hc") else getattr(c, f)) for f in diff},
                "ref_line": r.lineno, "cand_line": c.lineno,
            }
    only_r = len(set(R) - set(C))
    only_c = len(set(C) - set(R))
    if subset:
        coverage_ok = min(only_r, only_c) == 0
    else:
        coverage_ok = only_r == 0 and only_c == 0
    ok = coverage_ok and matched == len(keys) and len(keys) > 0
    return CompareResult(ok, len(keys), matched, only_r, only_c, first,
                         "subset" if subset else "exact")


# ---------------------------------------------------------------------------
# Batched (multi-stream) logs, format v1-batch.  See SPEC.md, "Batched logs".
#
#     <s> <pi> <j> <h> <hc> [<freq> <total>]    one line per token of stream s
#                                               (hash-only form: first 5 fields)
#     ALL <s> <16 hex>                          chain of stream s, in file order
#
# Stream ids >= FILLER_BASE mark filler work that occupied a slot before a
# staggered stream joined.  Filler rows have no ALL line; they are compared
# against the reference like every other row.

FILLER_BASE = 1000


@dataclasses.dataclass
class BatchLog:
    path: str
    rows: List[Tuple[int, TokenLine]]          # (stream, token line), file order
    all_by_stream: Dict[int, str]
    errors: List[str]

    def streams(self) -> List[int]:
        return sorted({s for s, _ in self.rows if s < FILLER_BASE})

    def chains(self) -> Dict[int, int]:
        acc: Dict[int, int] = {}
        for s, t in self.rows:
            if s >= FILLER_BASE:
                continue
            a = acc.get(s, FNV_OFFSET)
            a = fnv1a64_u64(t.h, a)
            acc[s] = fnv1a64_u64(t.hc, a)
        return acc


def parse_batch_log(path: str, lines: Optional[Iterable[str]] = None) -> BatchLog:
    if lines is None:
        lines = read_lines(path)
    rows: List[Tuple[int, TokenLine]] = []
    alls: Dict[int, str] = {}
    errors: List[str] = []
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "ALL":
            if len(p) != 3 or not p[1].isdigit() or len(p[2]) != 16:
                errors.append(f"line {n}: malformed batch ALL line")
                continue
            sid = int(p[1])
            if sid in alls:
                errors.append(f"line {n}: second ALL line for stream {sid}")
            alls[sid] = p[2].lower()
            continue
        if not p[0].isdigit():
            continue  # reserved keyword line
        if len(p) not in (5, 7):
            errors.append(f"line {n}: expected 7 fields (or 5 in a hash-only log), got {len(p)}")
            continue
        try:
            sid, pi, j = int(p[0]), int(p[1]), int(p[2])
            if len(p[3]) != 16 or len(p[4]) != 16:
                raise ValueError("hash field is not 16 hex digits")
            h, hc = int(p[3], 16), int(p[4], 16)
            freq = total = None
            if len(p) == 7:
                freq, total = int(p[5]), int(p[6])
        except ValueError as e:
            errors.append(f"line {n}: {e}")
            continue
        if total is not None and not (total > 0):
            errors.append(f"line {n}: legacy field total {total} out of range")
        if freq is not None and total is not None and not (0 < freq <= total):
            errors.append(f"line {n}: freq {freq} not in (0, total]")
        rows.append((sid, TokenLine(pi, j, h, hc, freq, total, n)))
    return BatchLog(path, rows, alls, errors)


def streams_digest(all_by_stream: Dict[int, str]) -> str:
    """One 64-bit summary of a batched log: fold over streams in ascending id of
    le64(stream id) then le64(ALL of that stream)."""
    a = FNV_OFFSET
    for sid in sorted(all_by_stream):
        a = fnv1a64_u64(sid, a)
        a = fnv1a64_u64(int(all_by_stream[sid], 16), a)
    return "%016x" % a


@dataclasses.dataclass
class BatchCheckResult:
    ok: bool
    n_streams: int
    n_rows: int
    n_filler_rows: int
    all_by_stream: Dict[int, str]
    streams_digest: str
    errors: List[str]


def check_batch_log(log: BatchLog) -> BatchCheckResult:
    errs = list(log.errors)
    rec = {s: "%016x" % v for s, v in log.chains().items()}
    for s in sorted(set(rec) | set(log.all_by_stream)):
        if s not in log.all_by_stream:
            errs.append(f"stream {s}: no ALL line")
        elif s not in rec:
            errs.append(f"stream {s}: ALL line but no token lines")
        elif rec[s] != log.all_by_stream[s]:
            errs.append(f"stream {s}: ALL mismatch: file says {log.all_by_stream[s]}, recomputed {rec[s]}")
    filler = sum(1 for s, _ in log.rows if s >= FILLER_BASE)
    return BatchCheckResult(not errs, len(rec), len(log.rows), filler, rec,
                            streams_digest(rec), errs)


@dataclasses.dataclass
class BatchCompareResult:
    ok: bool
    compared: int
    matched: int
    missing_in_ref: int
    first_divergence: Optional[dict]


def compare_batch(ref: Log, batch: BatchLog) -> BatchCompareResult:
    """Every row of every stream (filler included) must equal the reference
    token line at the same (payload, position)."""
    R = ref.by_key()
    matched = missing = 0
    first = None
    for sid, t in batch.rows:
        r = R.get(t.key)
        if r is None:
            missing += 1
            if first is None:
                first = {"stream": sid, "pi": t.pi, "j": t.j, "fields": ["missing in reference"],
                         "cand_line": t.lineno}
            continue
        diff = _diff_fields(r, t)
        if not diff:
            matched += 1
        elif first is None:
            first = {"stream": sid, "pi": t.pi, "j": t.j, "fields": diff,
                     "ref_line": r.lineno, "cand_line": t.lineno}
    ok = missing == 0 and matched == len(batch.rows) and matched > 0
    return BatchCompareResult(ok, len(batch.rows), matched, missing, first)
