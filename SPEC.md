# Idemcore hash log formats

Status: draft. Two formats are defined:

* **Format v2** (`idemcore-log/v2`, verifier 0.3.7 and later) uses SHA-256
  for every per-position digest and for the chain. It is the recommended
  format for new logs.
* **Format v1** (legacy 64-bit checksum format) is the format of every log
  published up to verifier 0.3.6. It stays supported unchanged: every
  published log keeps verifying with every later verifier.

The verifier treats every per-position digest as an opaque value. It never
needs the data a digest was computed from; it only compares digests and
chains them.

## Format v2 (recommended)

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
* Exactly one `CHAIN` line. v1 lines (`ALL`, `SEAL`, six-field lines) are not
  valid in a v2 log.

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
A v2 log is never compared against a v1 log: the verifier reports a format
mismatch instead.

### Example

[tests/vectors/v2_example.log](tests/vectors/v2_example.log) is a synthetic
test vector (not a model run) with eight positions and
`CHAIN f4ce37fdf9cbcb300331d0c8e04cca6586276e0365156d009f6d89ef342c8a6c`.

## Format v1 (legacy 64-bit checksum format)

### Per-position line

```
<pi> <j> <h> <hc> [<freq> <total>]
```

| field | type | meaning |
|---|---|---|
| `pi` | decimal | payload (sequence / request) index |
| `j` | decimal | position inside the payload (0-based) |
| `h` | 16 hex | 64-bit digest of the engine's complete output at this position |
| `hc` | 16 hex | 64-bit digest of the engine's choice output at this position |
| `freq` | decimal | optional legacy field (logs written before verifier 0.3.2) |
| `total` | decimal | optional legacy field (logs written before verifier 0.3.2) |

`freq` and `total` are optional legacy fields: when present, the verifier
checks that they are well-formed and compares them verbatim between logs that
both carry them. They are not part of any digest.

A hash-only log (`log_format` `idemcore-log/r1-public`) carries only the
first four fields of each line. The hosted API serves this form, and the
sample logs in `samples/` are published in it (since verifier 0.3.2). When
two lines are compared and either of them is hash-only, only `h` and `hc`
are compared.

### Chain line

```
ALL <16 hex>
```

`ALL` is a legacy 64-bit chained checksum over the `h` and `hc` values of all
position lines, in file order. Its exact definition is the reference
function `Log.chain()` in [idemcore_verify/core.py](idemcore_verify/core.py),
with test vectors in [tests/test_verify.py](tests/test_verify.py). It is
frozen: it detects accidental divergence and any edit to a published log,
but it is **not** collision-resistant against an adversary who can choose
the logged values. Use format v2 (or a v1 log with a `SEAL` line, below)
where that matters.

### Optional SEAL line (verifier 0.3.7 and later)

```
SEAL <64 hex>
SEAL = SHA-256( "idemcore-log/v1-seal\n" || L1 || ... || Ln )
```

where `Li` is `"<pi> <j> <h> <hc>\n"` for the i-th position line in file
order (decimal without leading zeros, 16 lowercase hex digits; legacy fields
dropped). A `SEAL` line adds a SHA-256 commitment to the positions, order and
digests of an existing v1 log without changing its `ALL` value. The per-
position digests themselves stay 64-bit. `idemcore-verify seal LOG -o OUT`
checks `ALL` and writes a copy with the `SEAL` line; `check` verifies a
`SEAL` line when present. Verifiers before 0.3.7 ignore the line.

## Lines common to both formats

* Lines starting with `#` are comments.
* Other lines that start with a keyword (not a number) are reserved for
  future versions and ignored by this verifier. Defined keywords:
  `FORMAT`, `ALL`, `CHAIN`, `SEAL`. `FORMAT idemcore-log/v1` may be written
  explicitly; a log without a `FORMAT` line is v1.
* Files may be gzipped (`.log.gz`).

## Batched logs

A server that runs `B` streams concurrently writes one file per run, with a
stream id in front of every position line.

Format v2:

```
FORMAT idemcore-log/v2
<s> <pi> <j> <h> <hc>
CHAIN <s> <64 hex>
```

Format v1:

```
<s> <pi> <j> <h> <hc> [<freq> <total>]
ALL <s> <16 hex>
```

* `s` (decimal) is the stream id. Fields after it are exactly as in the
  single-stream line of the same format.
* `CHAIN <s>` / `ALL <s>` is the chained digest of stream `s`, computed as for
  a single-stream log over that stream's lines in file order (lines of other
  streams are skipped; the stream id is not part of the hashed line). One
  digest line per stream.
* Stream ids `≥ 1000` are filler: short warm-up streams that occupy a slot
  before a staggered join. They have no digest line, but every one of their
  position lines is still compared against the reference.
* A stream may revisit the same `(pi, j)` (requests are re-issued in staggered
  schedules); every occurrence must match the reference.
* `STREAMS` digest (not stored in the file, computed by the verifier): one
  summary over `(s, digest of s)` for every stream with a digest line, in
  ascending `s`.
  * v2: `SHA-256( "idemcore-log/v2-streams\n" || for each s: "<s> <CHAIN[s]>\n" )`
  * v1: the legacy 64-bit checksum, see `streams_digest()` in
    [idemcore_verify/core.py](idemcore_verify/core.py).

`python3 -m idemcore_verify check-batch` recomputes every stream's digest and
the `STREAMS` digest; `compare-batch REF BATCH` checks every row of `BATCH`
against a single-stream reference of the same format keyed by `(pi, j)`.

## Producing a log from your own engine

Nothing in the format is specific to Idemcore. Any engine can emit format v2:
serialize its complete output at each position to bytes in a fixed, documented
way, write the SHA-256 of those bytes as `h`, and either write the SHA-256 of
its choice output as `hc` or the SHA-256 of the empty string. Then write the
`FORMAT` line first and the `CHAIN` line last. `idemcore_verify.core.format_v2_log()`
is a reference writer, and `step_digest()` computes one digest. That is
enough to test an engine's run-to-run and cross-device reproducibility with
this tool.
