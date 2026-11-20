# SPDX-License-Identifier: Apache-2.0
"""Parsing and checking of per-position hash logs, format v2 (``idemcore-log/v2``).

See SPEC.md for the normative text.

    FORMAT idemcore-log/v2
    <pi> <j> <h> <hc>          h, hc: SHA-256 digests, 64 lowercase hex
    CHAIN <64 hex>             SHA-256 over the format tag and every position
                               line, in file order

  pi   payload (sequence / request) index, decimal
  j    position inside the payload, decimal
  h    SHA-256 of the engine's complete output at this position
  hc   SHA-256 of the engine's choice output at this position (or of the
       empty string when the engine records none)

Lines starting with ``#`` are comments. Other lines that start with a keyword
(not a number) are reserved and ignored. Logs written in the earlier format
(no ``FORMAT idemcore-log/v2`` line) are reported as legacy and not checked.
"""
from __future__ import annotations

import dataclasses
import gzip
import hashlib
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

V2 = "v2"
V2_TAG = "idemcore-log/v2"
V2_STREAMS_TAG = "idemcore-log/v2-streams"
FILLER_BASE = 1000
LEGACY = "legacy"
LEGACY_MESSAGE = ("not a format v2 log (no 'FORMAT idemcore-log/v2' line): this looks like a log in the "
                  "earlier format, which this verifier no longer checks; use the re-issued format v2 "
                  "log of the same run")

_DEC = re.compile(r"(0|[1-9][0-9]*)\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def step_digest(data: bytes) -> str:
    """SHA-256 of a byte string as 64 lowercase hex: the value an engine
    writes into the h / hc field of a position line."""
    return hashlib.sha256(data).hexdigest()


EMPTY_DIGEST = step_digest(b"")


def canonical_line(pi: int, j: int, h: str, hc: str) -> str:
    return f"{pi} {j} {h} {hc}\n"


def chain_v2(lines: Iterable[str], tag: str = V2_TAG) -> str:
    """SHA-256 over ``tag + "\\n"`` followed by the canonical position lines."""
    m = hashlib.sha256((tag + "\n").encode("ascii"))
    for ln in lines:
        m.update(ln.encode("ascii"))
    return m.hexdigest()


def format_v2_log(rows: Iterable[Tuple[int, int, str, str]], comments: Sequence[str] = ()) -> str:
    """Reference writer. rows: (pi, j, h_hex64, hc_hex64) in the order the
    engine produced them. Returns the complete log text."""
    body = []
    for pi, j, h, hc in rows:
        h, hc = h.lower(), hc.lower()
        if not (_HEX64.match(h) and _HEX64.match(hc)):
            raise ValueError("digests are 64 hex digits")
        if int(pi) < 0 or int(j) < 0:
            raise ValueError("pi and j are non-negative")
        body.append(canonical_line(int(pi), int(j), h, hc))
    return "".join([f"# {c}\n" for c in comments] + [f"FORMAT {V2_TAG}\n"] + body + [f"CHAIN {chain_v2(body)}\n"])


def read_lines(path: str) -> List[str]:
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="ascii", newline="") as f:
        text = f.read()
    return text.split("\n")[:-1] if text.endswith("\n") else text.split("\n")


@dataclasses.dataclass(frozen=True)
class PositionLine:
    pi: int
    j: int
    h: str
    hc: str
    lineno: int

    @property
    def key(self) -> Tuple[int, int]:
        return (self.pi, self.j)

    def canonical(self) -> str:
        return canonical_line(self.pi, self.j, self.h, self.hc)


def _parse_position(fields: List[str], n: int, errors: List[str]) -> Optional[PositionLine]:
    if len(fields) != 4:
        errors.append(f"line {n}: expected 4 fields '<pi> <j> <h> <hc>', got {len(fields)}")
        return None
    pi, j, h, hc = fields
    if not (_DEC.match(pi) and _DEC.match(j)):
        errors.append(f"line {n}: pi and j must be decimal without leading zeros")
        return None
    if not (_HEX64.match(h) and _HEX64.match(hc)):
        errors.append(f"line {n}: h and hc must be 64 lowercase hex digits")
        return None
    return PositionLine(int(pi), int(j), h, hc, n)


def _header_and_body(lines: List[str], errors: List[str]):
    """Yield (lineno, fields) for non-comment lines after checking the FORMAT line."""
    fmt_seen = False
    out = []
    for n, raw in enumerate(lines, 1):
        if raw.endswith("\r"):
            errors.append(f"line {n}: CRLF line ending (lines end in LF)")
            raw = raw[:-1]
        if raw == "" or raw.startswith("#"):
            continue
        if raw != raw.strip() or "  " in raw or "\t" in raw:
            errors.append(f"line {n}: not in canonical form (single spaces, no leading/trailing space)")
        f = raw.split()
        if not f:
            continue
        if f[0] == "FORMAT":
            if fmt_seen:
                errors.append(f"line {n}: second FORMAT line")
            elif out:
                errors.append(f"line {n}: FORMAT line after position lines")
            elif f[1:] != [V2_TAG]:
                errors.append(f"line {n}: unsupported format {' '.join(f[1:])!r}")
            fmt_seen = True
            continue
        if not fmt_seen and not out:
            # first non-comment line is not FORMAT: earlier format
            return False, []
        out.append((n, f))
    return fmt_seen, out


@dataclasses.dataclass
class Log:
    path: str
    positions: List[PositionLine]
    chain_hex: Optional[str]
    errors: List[str]
    legacy: bool = False

    def canonical_lines(self) -> List[str]:
        return [t.canonical() for t in self.positions]

    def chain(self) -> str:
        return chain_v2(self.canonical_lines())

    def by_key(self) -> Dict[Tuple[int, int], PositionLine]:
        return {t.key: t for t in self.positions}


def parse_log(path: str, lines: Optional[List[str]] = None) -> Log:
    """Parse a single-stream log from a file (or from ``lines`` when given)."""
    errors: List[str] = []
    try:
        lines = read_lines(path) if lines is None else lines
    except UnicodeDecodeError:
        return Log(path, [], None, ["file is not ASCII text"])
    ok, body = _header_and_body(lines, errors)
    if not ok:
        return Log(path, [], None, [LEGACY_MESSAGE], legacy=True)
    pos: List[PositionLine] = []
    chain = None
    seen = set()
    for n, f in body:
        if f[0] == "CHAIN":
            if chain is not None:
                errors.append(f"line {n}: second CHAIN line")
            elif len(f) != 2 or not _HEX64.match(f[1]):
                errors.append(f"line {n}: malformed CHAIN line")
            else:
                chain = f[1]
            continue
        if f[0] in ("ALL", "SEAL"):
            errors.append(f"line {n}: {f[0]} lines are not valid in a format v2 log")
            continue
        if not f[0][:1].isdigit():
            continue  # reserved keyword line
        if chain is not None:
            errors.append(f"line {n}: position line after CHAIN")
        t = _parse_position(f, n, errors)
        if t is None:
            continue
        if t.key in seen:
            errors.append(f"line {n}: duplicate position (pi {t.pi}, j {t.j})")
        seen.add(t.key)
        pos.append(t)
    if chain is None:
        errors.append("no CHAIN line")
    return Log(path, pos, chain, errors)


@dataclasses.dataclass
class CheckResult:
    ok: bool
    n_positions: int
    chain_claimed: Optional[str]
    chain_recomputed: str
    errors: List[str]
    format: str = V2


def check_log(log: Log) -> CheckResult:
    errs = list(log.errors)
    rec = log.chain()
    if log.legacy:
        return CheckResult(False, 0, None, "-", errs, LEGACY)
    if not log.positions:
        errs.append("no position lines")
    if log.chain_hex is not None and log.chain_hex != rec:
        errs.append(f"CHAIN mismatch: file says {log.chain_hex}, recomputed {rec}")
    return CheckResult(not errs, len(log.positions), log.chain_hex, rec, errs)


@dataclasses.dataclass
class CompareResult:
    ok: bool
    mode: str
    compared: int
    matched: int
    only_in_ref: int
    only_in_cand: int
    first_divergence: Optional[dict]
    error: Optional[str] = None


def _diff_fields(r: PositionLine, c: PositionLine) -> List[str]:
    return [k for k in ("h", "hc") if getattr(r, k) != getattr(c, k)]


def compare_logs(ref: Log, cand: Log, subset: bool = False) -> CompareResult:
    """exact: same positions in the same order, every line equal.
    subset: compare the positions both logs cover; one must be contained in the other."""
    mode = "subset" if subset else "exact"
    if ref.legacy or cand.legacy:
        return CompareResult(False, mode, 0, 0, 0, 0, None, LEGACY_MESSAGE)
    R, C = ref.by_key(), cand.by_key()
    only_r = len(set(R) - set(C))
    only_c = len(set(C) - set(R))
    first = None
    matched = compared = 0
    if subset:
        keys = [t.key for t in ref.positions if t.key in C]
        if only_r and only_c:
            return CompareResult(False, mode, 0, 0, only_r, only_c, None,
                                 "neither log's positions are contained in the other's")
    else:
        if [t.key for t in ref.positions] != [t.key for t in cand.positions]:
            return CompareResult(False, mode, 0, 0, only_r, only_c, None,
                                 "logs cover different positions or a different order; use --subset for a spot check")
        keys = [t.key for t in ref.positions]
    for k in keys:
        compared += 1
        d = _diff_fields(R[k], C[k])
        if not d:
            matched += 1
        elif first is None:
            first = {"pi": k[0], "j": k[1], "fields": d, "ref_line": R[k].lineno, "cand_line": C[k].lineno,
                     "ref": R[k].canonical().strip(), "cand": C[k].canonical().strip()}
    ok = compared > 0 and matched == compared
    return CompareResult(ok, mode, compared, matched, only_r, only_c, first)


# ---------------------------------------------------------------------------
# Batched logs: one file per run of B concurrent streams.
#   FORMAT idemcore-log/v2
#   <s> <pi> <j> <h> <hc>
#   CHAIN <s> <64 hex>

@dataclasses.dataclass
class BatchLog:
    path: str
    rows: List[Tuple[int, PositionLine]]
    chain_by_stream: Dict[int, str]
    errors: List[str]
    legacy: bool = False

    def chains(self) -> Dict[int, str]:
        per: Dict[int, List[str]] = {}
        for s, t in self.rows:
            if s < FILLER_BASE:
                per.setdefault(s, []).append(t.canonical())
        return {s: chain_v2(v) for s, v in per.items()}


def parse_batch_log(path: str, lines: Optional[List[str]] = None) -> BatchLog:
    errors: List[str] = []
    lines = read_lines(path) if lines is None else lines
    ok, body = _header_and_body(lines, errors)
    if not ok:
        return BatchLog(path, [], {}, [LEGACY_MESSAGE], legacy=True)
    rows: List[Tuple[int, PositionLine]] = []
    chains: Dict[int, str] = {}
    for n, f in body:
        if f[0] == "CHAIN":
            if len(f) != 3 or not _DEC.match(f[1]) or not _HEX64.match(f[2]):
                errors.append(f"line {n}: malformed CHAIN line")
            elif int(f[1]) in chains:
                errors.append(f"line {n}: second CHAIN line for stream {f[1]}")
            else:
                chains[int(f[1])] = f[2]
            continue
        if f[0] in ("ALL", "SEAL"):
            errors.append(f"line {n}: {f[0]} lines are not valid in a format v2 log")
            continue
        if not f[0][:1].isdigit():
            continue
        if not _DEC.match(f[0]):
            errors.append(f"line {n}: stream id must be decimal")
            continue
        t = _parse_position(f[1:], n, errors)
        if t is not None:
            rows.append((int(f[0]), t))
    return BatchLog(path, rows, chains, errors)


def streams_digest(chain_by_stream: Dict[int, str]) -> str:
    return chain_v2((f"{s} {chain_by_stream[s]}\n" for s in sorted(chain_by_stream)), V2_STREAMS_TAG)


@dataclasses.dataclass
class BatchCheckResult:
    ok: bool
    n_streams: int
    n_rows: int
    n_filler_rows: int
    chain_by_stream: Dict[int, str]
    streams_digest: str
    errors: List[str]
    format: str = V2


def check_batch_log(log: BatchLog) -> BatchCheckResult:
    errs = list(log.errors)
    if log.legacy:
        return BatchCheckResult(False, 0, 0, 0, {}, "-", errs, LEGACY)
    rec = log.chains()
    for s in sorted(set(rec) | set(log.chain_by_stream)):
        if s not in log.chain_by_stream:
            errs.append(f"stream {s}: no CHAIN line")
        elif s not in rec:
            errs.append(f"stream {s}: CHAIN line but no position lines")
        elif rec[s] != log.chain_by_stream[s]:
            errs.append(f"stream {s}: CHAIN mismatch: file says {log.chain_by_stream[s]}, recomputed {rec[s]}")
    if not log.rows:
        errs.append("no position lines")
    filler = sum(1 for s, _ in log.rows if s >= FILLER_BASE)
    return BatchCheckResult(not errs, len(rec), len(log.rows), filler, rec, streams_digest(rec), errs)


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
    if ref.legacy or batch.legacy:
        return BatchCompareResult(False, 0, 0, 0, None, LEGACY_MESSAGE)
    R = ref.by_key()
    matched = missing = 0
    first = None
    for sid, t in batch.rows:
        r = R.get(t.key)
        if r is None:
            missing += 1
            if first is None:
                first = {"stream": sid, "pi": t.pi, "j": t.j, "fields": ["missing in reference"], "cand_line": t.lineno}
            continue
        d = _diff_fields(r, t)
        if not d:
            matched += 1
        elif first is None:
            first = {"stream": sid, "pi": t.pi, "j": t.j, "fields": d, "ref_line": r.lineno, "cand_line": t.lineno}
    ok = missing == 0 and matched == len(batch.rows) and matched > 0
    return BatchCompareResult(ok, len(batch.rows), matched, missing, first)
