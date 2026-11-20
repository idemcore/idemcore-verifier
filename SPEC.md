# Idemcore hash log format

Status: draft. This verifier (0.4.0 and later) checks one format:
**format v2** (`idemcore-log/v2`), which uses SHA-256 for every per-position
digest and for the chain.

Logs written in the earlier format (no `FORMAT idemcore-log/v2` line, `ALL`
chain line) are no longer checked by this verifier: it reports them as not
format v2. Published logs have been re-issued in format v2; see
[EVIDENCE.md](EVIDENCE.md) for the list and the few still pending.

The verifier treats every per-position digest as an opaque value. It never
needs the data a digest was computed from; it only compares digests and
chains them.

## Format v2

### Lines

```
FORMAT idemcore-log/v2
<pi> <j> <h> <hc>
...
CHAIN <64 hex>
```

| field | type | meaning |
|---|---|---|
| `pi` | decimal | payload (sequence / request) index |
| `j` | decimal | position inside the payload (0-based) |
| `h` | 64 hex | SHA-256 digest of the engine's complete output at this position |
| `hc` | 64 hex | SHA-256 digest of the engine's choice output at this position, or the SHA-256 of the empty string (`e3b0c442…b855`) when the engine records none |

Rules:

* The `FORMAT idemcore-log/v2` line comes before the first position line.
  Comment lines (`#`) may precede it.
* Position lines are in **canonical form**: decimal `pi` and `j` without
  leading zeros, lowercase hex, exactly one space between fields, no
  trailing spaces. Lines end in LF.
* A `(pi, j)` pair appears at most once.
* Exactly one `CHAIN` line. Five- or six-field position lines, 16-hex digests
  and `ALL` / `SEAL` lines are not valid in a v2 log.

### Chain

```
CHAIN = SHA-256( "idemcore-log/v2\n" || L1 || L2 || ... || Ln )
```

where `Li` is the i-th position line in file order, in canonical form,
including its trailing `\n`. Because the chain covers `pi` and `j` as well
as both digests, it commits to which positions were logged, their order and
every digest. Any change to a position line changes `CHAIN`.

Anyone can recompute it with standard tools, without this verifier:

```sh
(printf 'idemcore-log/v2\n'; grep -E '^[0-9]' run.log) | sha256sum
```

### Comparing two v2 logs

Two runs agree at a position when both `h` and `hc` are equal. Two logs over
the same positions in the same order have equal `CHAIN` exactly when every
line is equal (up to SHA-256 collisions). Logs that cover different subsets
have different `CHAIN` values; compare them line by line with `--subset`.
A log that is not format v2 is reported as such and never compared.

### Example

[tests/vectors/v2_example.log](tests/vectors/v2_example.log) is a synthetic
test vector (not a model run) with eight positions and
`CHAIN f4ce37fdf9cbcb300331d0c8e04cca6586276e0365156d009f6d89ef342c8a6c`.

## Other lines

* Lines starting with `#` are comments.
* Other lines that start with a keyword (not a number) are reserved for
  future versions and ignored. Defined keywords: `FORMAT`, `CHAIN`.
* Files may be gzipped (`.log.gz`).

## Batched logs

A server that runs `B` streams concurrently writes one file per run, with a
stream id in front of every position line:

```
FORMAT idemcore-log/v2
<s> <pi> <j> <h> <hc>
CHAIN <s> <64 hex>
```

* `s` (decimal) is the stream id. Fields after it are exactly as in the
  single-stream line.
* `CHAIN <s>` is the chain of stream `s`, computed as for a single-stream log
  over that stream's lines in file order (lines of other streams are skipped;
  the stream id is not part of the hashed line). One `CHAIN` line per stream.
* Stream ids `≥ 1000` are filler: short warm-up streams that occupy a slot
  before a staggered join. They have no `CHAIN` line, but every one of their
  position lines is still compared against the reference.
* A stream may revisit the same `(pi, j)` (requests are re-issued in staggered
  schedules); every occurrence must match the reference.
* `STREAMS` digest (not stored in the file, computed by the verifier):
  `SHA-256( "idemcore-log/v2-streams\n" || for each s: "<s> <CHAIN[s]>\n" )`
  over every stream with a `CHAIN` line, in ascending `s`.

`python3 -m idemcore_verify check-batch` recomputes every stream's chain and
the `STREAMS` digest; `compare-batch REF BATCH` checks every row of `BATCH`
against a single-stream reference keyed by `(pi, j)`.

## Producing a log from your own engine

Nothing in the format is specific to Idemcore. Any engine can emit format v2:
serialize its complete output at each position to bytes in a fixed, documented
way, write the SHA-256 of those bytes as `h`, and either write the SHA-256 of
its choice output as `hc` or the SHA-256 of the empty string. Then write the
`FORMAT` line first and the `CHAIN` line last. `idemcore_verify.core.format_v2_log()`
is a reference writer, and `step_digest()` computes one digest. That is
enough to test an engine's run-to-run and cross-device reproducibility with
this tool.
