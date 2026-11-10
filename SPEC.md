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
| `h` | 16 hex | 64-bit hash of the engine's output (logits) over the whole vocabulary at this position |
| `hc` | 16 hex | second 64-bit hash, over the engine's token-choice output at this position |
| `freq` | decimal | optional legacy field (logs written before verifier 0.3.2) |
| `total` | decimal | optional legacy field (logs written before verifier 0.3.2) |

The verifier treats `h` and `hc` as opaque 64-bit values: it never needs the
values they were computed from, only compares them and chains them into `ALL`.
`freq` and `total` are optional legacy fields: when present, the verifier checks
that they are well-formed and compares them verbatim between logs that both
carry them. They are not part of `ALL`.

FNV-1a-64: offset basis `0xcbf29ce484222325`, prime `0x100000001b3`,
`h = (h XOR byte) * prime mod 2^64` per byte.

## Hash-only (public) form

A hash-only log (`log_format` `idemcore-log/r1-public`) carries only the first
four fields of each per-token line:

```
<pi> <j> <h> <hc>
```

The hosted API serves this form, and the sample logs in `samples/` are
published in it (since verifier 0.3.2). The `ALL` line below depends only on
`h` and `hc`, so it is identical for the full and the hash-only form of the
same run. When two lines are compared and either of them is hash-only, only
`h` and `hc` are compared. The verifier keeps accepting six-field logs.

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
  per-token line above, in full (`<freq> <total>` present, 7 fields) or
  hash-only form (`<s> <pi> <j> <h> <hc>`, 5 fields).
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

Files may be gzipped (`.log.gz`). `python3 -m idemcore_verify
check-batch` recomputes every stream's `ALL` and the `STREAMS` digest;
`compare-batch REF BATCH` checks every row of `BATCH` against a single-stream
reference keyed by `(pi, j)`.

## Producing a log from your own engine

Nothing in the format is specific to Idemcore. Any engine can emit it: hash
the raw bytes of its logit vector with FNV-1a-64 (`h`) and either hash its
token-choice state (`hc`) or leave `hc` as the hash of an empty buffer, which
already lets you test its run-to-run and cross-device reproducibility with
this tool.
