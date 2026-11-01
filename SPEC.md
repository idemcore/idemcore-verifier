# Idemcore hash log format, version 1

Status: draft. Byte order is little-endian throughout.

## Per-token line

```
<pi> <j> <h> <hc> <freq> <total>
```

| field | type | meaning |
|---|---|---|
| `pi` | decimal | payload (sequence / request) index |
| `j` | decimal | position inside the payload (0-based) |
| `h` | 16 hex | FNV-1a-64 over the `V` logits, each a signed 32-bit integer, LE, in vocabulary order |
| `hc` | 16 hex | FNV-1a-64 over the `V+1` cumulative-frequency entries `CUM[0..V]`, each an unsigned 64-bit integer, LE |
| `freq` | decimal | `CUM[t+1] - CUM[t]`, where `t` is the token actually observed / emitted at this position |
| `total` | decimal | `CUM[V]`; always `0 < total < 2^31` |

`V` is the model's vocabulary size (151 936 for Qwen2.5-0.5B, 152 064 for Qwen2.5-7B, 201 088 for gpt-oss).
`CUM` is the integer sampling table: `CUM[0] = 0`, non-decreasing, every token
has width ≥ 1. The probability the engine assigns to token `t` is exactly
`freq / total` — a rational number, identical on every device.

FNV-1a-64: offset basis `0xcbf29ce484222325`, prime `0x100000001b3`,
`h = (h XOR byte) * prime mod 2^64` per byte.

## Chain line

```
ALL <16 hex>
```

```
a = 0xcbf29ce484222325
for each per-token line, in file order:
    a = FNV1a64(le64(h),  start=a)
    a = FNV1a64(le64(hc), start=a)
```

`ALL` commits to the order of the lines. Two logs over the same positions in
the same order have equal `ALL` iff (up to FNV collisions) every `h` and `hc`
are equal. Logs that cover different subsets have different `ALL`; compare them
line-by-line with `--subset`.

## Optional lines

* Lines starting with `#` are comments.
* Other lines that start with a keyword (not a number) are reserved for
  future versions and ignored by this verifier.

## Batched logs

A server that runs `B` streams concurrently writes one file per run, with a
stream id in front of every per-token line:

```
<s> <pi> <j> <h> <hc> <freq> <total>
ALL <s> <16 hex>
```

* `s` (decimal) is the stream id. Fields after it are exactly as in the
  per-token line above.
* `ALL <s>` is the chained digest of stream `s`, computed as in the chain
  line over that stream's lines in file order (lines of other streams are
  skipped). One `ALL <s>` line per stream.
* Stream ids `≥ 1000` are filler: short warm-up streams that occupy a slot
  before a staggered join. They have no `ALL` line, but every one of their
  per-token lines is still compared against the reference.
* A stream may revisit the same `(pi, j)` (requests are re-issued in staggered
  schedules); every occurrence must match the reference.
* `STREAMS` digest (not stored in the file, computed by the verifier):

  ```
  a = 0xcbf29ce484222325
  for each stream s with an ALL line, in ascending s:
      a = FNV1a64(le64(s),      start=a)
      a = FNV1a64(le64(ALL[s]), start=a)
  ```

Files may be gzip-compressed (`.log.gz`). `python3 -m idemcore_verify
check-batch` recomputes every stream's `ALL` and the `STREAMS` digest;
`compare-batch REF BATCH` checks every row of `BATCH` against a single-stream
reference keyed by `(pi, j)`.

## Producing a log from your own engine

Nothing in the format is specific to Idemcore. Any engine that exposes
integer logits and an integer CDF can emit it; floating-point engines can hash
the raw bit patterns of their fp32 logits (`h`) and leave `hc` as the hash of
an empty buffer, which already lets you test their run-to-run and
cross-device reproducibility with this tool.
