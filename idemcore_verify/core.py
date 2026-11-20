# SPDX-License-Identifier: Apache-2.0
"""Parsing and checking of Idemcore per-position hash logs.

Two log formats are supported. See SPEC.md for the normative text.

Format v2 (``idemcore-log/v2``, recommended, verifier 0.3.7 and later)
    FORMAT idemcore-log/v2
    <pi> <j> <h> <hc>          h, hc: SHA-256 digests, 64 lowercase hex
    CHAIN <64 hex>             SHA-256 over the format tag and every
                               position line, in file order

Format v1 (legacy 64-bit checksum format, all logs published up to 0.3.6)
    <pi> <j> <h> <hc> [<freq> <total>]   h, hc: 64-bit values, 16 hex
    ALL <16 hex>                          legacy 64-bit chained checksum
    SEAL <64 hex>                         optional (0.3.7+): SHA-256 seal of
                                          the position lines, see SPEC.md

  pi     payload (sequence) index, decimal
  j      position inside the payload, decimal
  h      digest of the engine's complete output at this position
  hc     digest of the engine's choice output at this position
  freq, total
         optional legacy fields (v1 logs written before 0.3.2); checked for
         well-formedness and compared verbatim, never part of a digest

Other lines that start with a keyword (not a number) are reserved for future
versions and ignored. Lines starting with ``#`` are comments.
"""
from __future__ import annotations

import dataclasses
import gzip
import hashlib
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

V1 = "v1"
V2 = "v2"
V1_TAG = "idemcore-log/v1"
V2_TAG = "idemcore-log/v2"
V2_STREAMS_TAG = "idemcore-log/v2-streams"
V1_SEAL_TAG = "idemcore-log/v1-seal"
HEXW = {V1: 16, V2: 64}

# ---------------------------------------------------------------------------
# Legacy 64-bit checksum of format v1 (frozen; kept only so that every log
# published up to 0.3.6 keeps verifying). New logs should use format v2.

_V1_BASIS = 0xCBF29CE484222325
_V1_MULT = 0x100000001B3
MASK64 = (1 << 64) - 1


def legacy_checksum64(data: bytes, h: int = _V1_BASIS) -> int:
    """Format v1 checksum over a byte string."""
    for b in data:
        h ^= b
        h = (h * _V1_MULT) & MASK64
    return h


def legacy_checksum64_word(v: int, h: int) -> int:
    """Format v1 checksum step over the 8 little-endian bytes of v."""
    for i in range(8):
        h ^= (v >> (8 * i)) & 0xFF
        h = (h * _V1_MULT) & MASK64
    return h


LEGACY_BASIS = _V1_BASIS

# Names used by verifier 0.3.6 and earlier, kept so that existing imports
# keep working. Not part of the documented interface.
_OLD_NAMES = {
    "fnv1a64": legacy_checksum64,
    "fnv1a64_u64": legacy_checksum64_word,
    "FNV_OFFSET": _V1_BASIS,
    "FNV_PRIME": _V1_MULT,
}


def __getattr__(name):  # PEP 562
    try:
        return _OLD_NAMES[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None


# ---------------------------------------------------------------------------
# Format v2 helpers (SHA-256)

def step_digest(data: bytes) -> str:
    """SHA-256 of a byte string as 64 lowercase hex: the value an engine
    writes into the h / hc field of a format v2 line."""
    return hashlib.sha256(data).hexdigest()


EMPTY_DIGEST = step_digest(b"")


def canonical_line(pi: int, j: int, h: int, hc: int, width: int) -> str:
    return f"{pi} {j} {h:0{width}x} {hc:0{width}x}\n"


def chain_v2(lines: Iterable[str], tag: str = V2_TAG) -> str:
    """SHA-256 over ``tag + "\\n"`` followed by the canonical position lines."""
    m = hashlib.sha256((tag + "\n").encode("ascii"))
    for ln in lines:
        m.update(ln.encode("ascii"))
    return m.hexdigest()


def format_v2_log(rows: Iterable[Tuple[int, int, str, str]],
                  comments: Sequence[str] = ()) -> str:
    """Reference writer for format v2. rows: (pi, j, h_hex64, hc_hex64) in
    the order the engine produced them. Returns the complete log text."""
    out = [f"# {c}\n" for c in comments] + [f"FORMAT {V2_TAG}\n"]
    body = []
    for pi, j, h, hc in rows:
        h, hc = h.lower(), hc.lower()
        if len(h) != 64 or len(hc) != 64:
            raise ValueError("format v2 digests are 64 hex digits")
        body.append(canonical_line(int(pi), int(j), int(h, 16), int(hc, 16), 64))
    return "".join(out + body + [f"CHAIN {chain_v2(body)}\n"])


def _is_hex(s: str, width: int) -> bool:
    return len(s) == width and all(c in "0123456789abcdefABCDEF" for c in s)


def _hexok(s: str, width: int, fmt: str) -> bool:
    """v2: strict hex. v1: the length check of verifier 0.3.6 (the value is
    then parsed with int(..., 16)), unchanged for backward compatibility."""
    return _is_hex(s, width) if fmt == V2 else len(s) == width


# ---------------------------------------------------------------------------
# Single-stream logs

@dataclasses.dataclass(frozen=True)
class PositionLine:
    """One position line."""
    pi: int
    j: int
    h: int
    hc: int
    freq: Optional[int]   # None in a hash-only line and in every v2 line
    total: Optional[int]
    lineno: int

    @property
    def key(self) -> Tuple[int, int]:
        return (self.pi, self.j)


TokenLine = PositionLine   # name used by 0.3.6 and earlier


@dataclasses.dataclass
class Log:
    path: str
    tokens: List[PositionLine]     # field name kept for compatibility
    all_hex: Optional[str]          # v1: ALL value; v2: CHAIN value
    errors: List[str]
    fmt: str = V1
    seal_hex: Optional[str] = None  # v1 only, optional SEAL line

    @property
    def positions(self) -> List[PositionLine]:
        return self.tokens

    @property
    def width(self) -> int:
        return HEXW[self.fmt]

    def canonical_lines(self) -> List[str]:
        w = self.width
        return [canonical_line(t.pi, t.j, t.h, t.hc, w) for t in self.tokens]

    def chain(self) -> int:
        """v1: the legacy 64-bit ALL value. v2: the SHA-256 CHAIN value."""
        if self.fmt == V2:
            return int(chain_v2(self.canonical_lines()), 16)
        a = _V1_BASIS
        for t in self.tokens:
            a = legacy_checksum64_word(t.h, a)
            a = legacy_checksum64_word(t.hc, a)
        return a

    def chain_hex(self) -> str:
        return "%0*x" % (self.width, self.chain())

    def seal(self) -> str:
        """SHA-256 seal of a v1 log's position lines (see SPEC.md)."""
        return chain_v2(self.canonical_lines(), V1_SEAL_TAG)

    def by_key(self) -> Dict[Tuple[int, int], PositionLine]:
        return {t.key: t for t in self.tokens}


def read_lines(path: str) -> List[str]:
    """Read a log as ASCII lines; files ending in .gz are read with gzip."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="ascii") as f:
        return f.read().splitlines()


def _detect_format(lines: List[str], errors: List[str]) -> str:
    for raw in lines:
        p = raw.split()
        if p and p[0] == "FORMAT":
            if len(p) == 2 and p[1] == V2_TAG:
                return V2
            if len(p) == 2 and p[1] == V1_TAG:
                return V1
            errors.append(f"unsupported FORMAT line: {raw.strip()[:80]}")
            return V2
        if p and p[0].isdigit():
            break
    return V1


def parse_log(path: str, lines: Optional[Iterable[str]] = None) -> Log:
    lines = list(read_lines(path) if lines is None else lines)
    rows_: List[PositionLine] = []
    errors: List[str] = []
    fmt = _detect_format(lines, errors)
    w = HEXW[fmt]
    digest_kw = "CHAIN" if fmt == V2 else "ALL"
    all_hex = seal_hex = None
    seen = set()
    n_format = 0
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "FORMAT":
            n_format += 1
            if n_format > 1:
                errors.append(f"line {n}: second FORMAT line")
            if rows_:
                errors.append(f"line {n}: FORMAT line after position lines")
            continue
        if p[0] in ("ALL", "CHAIN"):
            if p[0] != digest_kw:
                errors.append(f"line {n}: {p[0]} line is not valid in a format {fmt} log")
                continue
            if fmt == V2 and all_hex is not None:
                errors.append(f"line {n}: second {digest_kw} line")
            if len(p) != 2 or not _hexok(p[1], w, fmt):
                errors.append(f"line {n}: malformed {digest_kw} line")
            all_hex = p[1].lower() if len(p) > 1 else ""
            continue
        if p[0] == "SEAL":
            if fmt == V2:
                errors.append(f"line {n}: SEAL line is not valid in a format v2 log")
            elif len(p) != 2 or not _is_hex(p[1], 64):
                errors.append(f"line {n}: malformed SEAL line")
            else:
                seal_hex = p[1].lower()
            continue
        if not p[0].isdigit():
            continue  # reserved keyword line
        allowed = (4,) if fmt == V2 else (4, 6)
        if len(p) not in allowed:
            want = "4 fields" if fmt == V2 else "6 fields (or 4 in a hash-only log)"
            errors.append(f"line {n}: expected {want}, got {len(p)}")
            continue
        try:
            pi, j = int(p[0]), int(p[1])
            if not (_hexok(p[2], w, fmt) and _hexok(p[3], w, fmt)):
                raise ValueError(f"hash field is not {w} hex digits")
            h, hc = int(p[2], 16), int(p[3], 16)
            freq = total = None
            if len(p) == 6:
                freq, total = int(p[4]), int(p[5])
        except ValueError as e:
            errors.append(f"line {n}: {e}")
            continue
        if fmt == V2 and raw != canonical_line(pi, j, h, hc, w)[:-1]:
            errors.append(f"line {n}: not in canonical form (single spaces, lowercase hex, "
                          "no leading zeros or padding)")
        if total is not None and not (total > 0):
            errors.append(f"line {n}: legacy field total {total} out of range")
        if freq is not None and total is not None and not (0 < freq <= total):
            errors.append(f"line {n}: freq {freq} not in (0, total]")
        if (pi, j) in seen:
            errors.append(f"line {n}: duplicate position ({pi},{j})")
        seen.add((pi, j))
        rows_.append(PositionLine(pi, j, h, hc, freq, total, n))
    if fmt == V2 and n_format == 0:
        errors.append("no FORMAT line")
    if all_hex is None:
        errors.append(f"no {digest_kw} line")
    return Log(path, rows_, all_hex, errors, fmt, seal_hex)


@dataclasses.dataclass
class CheckResult:
    ok: bool
    n_tokens: int                 # number of position lines
    all_claimed: Optional[str]    # v1: ALL in the file; v2: CHAIN in the file
    all_recomputed: str
    errors: List[str]
    format: str = V1
    seal: Optional[str] = None    # v1: SEAL recomputed when the file has one


def check_log(log: Log) -> CheckResult:
    rec = log.chain_hex()
    errs = list(log.errors)
    kw = "CHAIN" if log.fmt == V2 else "ALL"
    if log.all_hex is not None and rec != log.all_hex:
        errs.append(f"{kw} mismatch: file says {log.all_hex}, recomputed {rec}")
    seal = None
    if log.seal_hex is not None:
        seal = log.seal()
        if seal != log.seal_hex:
            errs.append(f"SEAL mismatch: file says {log.seal_hex}, recomputed {seal}")
    return CheckResult(not errs, len(log.tokens), log.all_hex, rec, errs, log.fmt, seal)


@dataclasses.dataclass
class CompareResult:
    ok: bool
    compared: int
    matched: int
    only_in_ref: int
    only_in_cand: int
    first_divergence: Optional[dict]
    mode: str
    error: Optional[str] = None


def _diff_fields(r: PositionLine, c: PositionLine) -> List[str]:
    """Fields that differ. freq/total are compared only when both lines carry
    them (a hash-only line has neither)."""
    out = [f for f in ("h", "hc") if getattr(r, f) != getattr(c, f)]
    if r.freq is not None and c.freq is not None:
        out += [f for f in ("freq", "total") if getattr(r, f) != getattr(c, f)]
    return out


def _fmt_fields(t: PositionLine, fields: List[str], width: int) -> dict:
    return {f: (("%0*x" % (width, getattr(t, f))) if f in ("h", "hc") else getattr(t, f))
            for f in fields}


def compare_logs(ref: Log, cand: Log, subset: bool = False) -> CompareResult:
    """Compare candidate against reference position by position.

    subset=False: both logs must cover exactly the same positions.
    subset=True : every position in the *smaller* log must appear, identical,
                  in the larger one (e.g. a CPU spot-check of a GPU run).
    Both logs must use the same format (v1 or v2).
    """
    mode = "subset" if subset else "exact"
    if ref.fmt != cand.fmt:
        return CompareResult(False, 0, 0, len(ref.tokens), len(cand.tokens), None, mode,
                             f"logs use different formats ({ref.fmt} vs {cand.fmt}); "
                             "compare two logs of the same format")
    w = ref.width
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
                "ref": _fmt_fields(r, diff, w), "cand": _fmt_fields(c, diff, w),
                "ref_line": r.lineno, "cand_line": c.lineno,
            }
    only_r = len(set(R) - set(C))
    only_c = len(set(C) - set(R))
    if subset:
        coverage_ok = min(only_r, only_c) == 0
    else:
        coverage_ok = only_r == 0 and only_c == 0
    ok = coverage_ok and matched == len(keys) and len(keys) > 0
    return CompareResult(ok, len(keys), matched, only_r, only_c, first, mode)


# ---------------------------------------------------------------------------
# Batched (multi-stream) logs.  See SPEC.md, "Batched logs".
#
#   v1:  <s> <pi> <j> <h> <hc> [<freq> <total>]    ALL <s> <16 hex>
#   v2:  FORMAT idemcore-log/v2
#        <s> <pi> <j> <h> <hc>                      CHAIN <s> <64 hex>
#
# Stream ids >= FILLER_BASE mark filler work that occupied a slot before a
# staggered stream joined.  Filler rows have no digest line; they are compared
# against the reference like every other row.

FILLER_BASE = 1000


@dataclasses.dataclass
class BatchLog:
    path: str
    rows: List[Tuple[int, PositionLine]]          # (stream, position line), file order
    all_by_stream: Dict[int, str]
    errors: List[str]
    fmt: str = V1

    def streams(self) -> List[int]:
        return sorted({s for s, _ in self.rows if s < FILLER_BASE})

    def chains(self) -> Dict[int, int]:
        if self.fmt == V2:
            per: Dict[int, List[str]] = {}
            for s, t in self.rows:
                if s < FILLER_BASE:
                    per.setdefault(s, []).append(canonical_line(t.pi, t.j, t.h, t.hc, 64))
            return {s: int(chain_v2(ls), 16) for s, ls in per.items()}
        acc: Dict[int, int] = {}
        for s, t in self.rows:
            if s >= FILLER_BASE:
                continue
            a = acc.get(s, _V1_BASIS)
            a = legacy_checksum64_word(t.h, a)
            acc[s] = legacy_checksum64_word(t.hc, a)
        return acc


def parse_batch_log(path: str, lines: Optional[Iterable[str]] = None) -> BatchLog:
    lines = list(read_lines(path) if lines is None else lines)
    rows: List[Tuple[int, PositionLine]] = []
    alls: Dict[int, str] = {}
    errors: List[str] = []
    fmt = _detect_format(lines, errors)
    w = HEXW[fmt]
    kw = "CHAIN" if fmt == V2 else "ALL"
    n_format = 0
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "FORMAT":
            n_format += 1
            if n_format > 1 or rows:
                errors.append(f"line {n}: misplaced FORMAT line")
            continue
        if p[0] in ("ALL", "CHAIN"):
            if p[0] != kw:
                errors.append(f"line {n}: {p[0]} line is not valid in a format {fmt} log")
                continue
            if len(p) != 3 or not p[1].isdigit() or not _hexok(p[2], w, fmt):
                errors.append(f"line {n}: malformed batch {kw} line")
                continue
            sid = int(p[1])
            if sid in alls:
                errors.append(f"line {n}: second {kw} line for stream {sid}")
            alls[sid] = p[2].lower()
            continue
        if not p[0].isdigit():
            continue  # reserved keyword line
        allowed = (5,) if fmt == V2 else (5, 7)
        if len(p) not in allowed:
            want = "5 fields" if fmt == V2 else "7 fields (or 5 in a hash-only log)"
            errors.append(f"line {n}: expected {want}, got {len(p)}")
            continue
        try:
            sid, pi, j = int(p[0]), int(p[1]), int(p[2])
            if not (_hexok(p[3], w, fmt) and _hexok(p[4], w, fmt)):
                raise ValueError(f"hash field is not {w} hex digits")
            h, hc = int(p[3], 16), int(p[4], 16)
            freq = total = None
            if len(p) == 7:
                freq, total = int(p[5]), int(p[6])
        except ValueError as e:
            errors.append(f"line {n}: {e}")
            continue
        if fmt == V2 and raw != f"{sid} " + canonical_line(pi, j, h, hc, w)[:-1]:
            errors.append(f"line {n}: not in canonical form")
        if total is not None and not (total > 0):
            errors.append(f"line {n}: legacy field total {total} out of range")
        if freq is not None and total is not None and not (0 < freq <= total):
            errors.append(f"line {n}: freq {freq} not in (0, total]")
        rows.append((sid, PositionLine(pi, j, h, hc, freq, total, n)))
    if fmt == V2 and n_format == 0:
        errors.append("no FORMAT line")
    return BatchLog(path, rows, alls, errors, fmt)


def streams_digest(all_by_stream: Dict[int, str], fmt: str = V1) -> str:
    """One summary digest of a batched log over (stream id, stream digest)
    pairs in ascending stream id. v1: legacy 64-bit; v2: SHA-256."""
    if fmt == V2:
        return chain_v2((f"{sid} {all_by_stream[sid]}\n" for sid in sorted(all_by_stream)),
                        V2_STREAMS_TAG)
    a = _V1_BASIS
    for sid in sorted(all_by_stream):
        a = legacy_checksum64_word(sid, a)
        a = legacy_checksum64_word(int(all_by_stream[sid], 16), a)
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
    format: str = V1


def check_batch_log(log: BatchLog) -> BatchCheckResult:
    errs = list(log.errors)
    w = HEXW[log.fmt]
    kw = "CHAIN" if log.fmt == V2 else "ALL"
    rec = {s: "%0*x" % (w, v) for s, v in log.chains().items()}
    for s in sorted(set(rec) | set(log.all_by_stream)):
        if s not in log.all_by_stream:
            errs.append(f"stream {s}: no {kw} line")
        elif s not in rec:
            errs.append(f"stream {s}: {kw} line but no position lines")
        elif rec[s] != log.all_by_stream[s]:
            errs.append(f"stream {s}: {kw} mismatch: file says {log.all_by_stream[s]}, recomputed {rec[s]}")
    filler = sum(1 for s, _ in log.rows if s >= FILLER_BASE)
    return BatchCheckResult(not errs, len(rec), len(log.rows), filler, rec,
                            streams_digest(rec, log.fmt), errs, log.fmt)


@dataclasses.dataclass
class BatchCompareResult:
    ok: bool
    compared: int
    matched: int
    missing_in_ref: int
    first_divergence: Optional[dict]
    error: Optional[str] = None


def compare_batch(ref: Log, batch: BatchLog) -> BatchCompareResult:
    """Every row of every stream (filler included) must equal the reference
    position line at the same (payload, position)."""
    if ref.fmt != batch.fmt:
        return BatchCompareResult(False, len(batch.rows), 0, 0, None,
                                  f"logs use different formats ({ref.fmt} vs {batch.fmt})")
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
