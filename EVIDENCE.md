# Evidence pack (format v2)

Every digest below is recomputed from the shipped logs by one command:

```sh
make verify            # or: python3 -m idemcore_verify samples
```

It reads [samples/HASHES.tsv](samples/HASHES.tsv) (the published `CHAIN`
values) and [samples/PAIRS.tsv](samples/PAIRS.tsv) (which log must match
which), recomputes every `CHAIN` from the position lines, re-compares every
pair, and prints `PASS` or `FAIL`. Standard library only.

## Re-issue status

Verifier 0.4.0 checks format v2 only. Published runs are re-issued as format
v2 logs of the same run (same model, same workload, same device class). A
re-issued log covers exactly the positions of the log it replaces.

### Available in format v2 now (x86-64 CPU)

| Model | Workload | Positions | CHAIN | File |
|---|---|---|---|---|
| Qwen2.5-0.5B 8-bit | W3260 | 3260 | `7fee20dbe7c0c8490add7a4392de187cc08fd303bbef914b6e1b98e9d8c3f065` | [x86_64.log](samples/qwen2.5-0.5b-int8/x86_64.log), [second run](samples/qwen2.5-0.5b-int8/x86_64_run2.log) |
| Qwen2.5-0.5B 8-bit | W240 | 240 | `224cc35af810655edb2071f2dea6e8575b2f6db81edfeb4851a7261328340027` | [x86_64_sub240.log](samples/qwen2.5-0.5b-int8/x86_64_sub240.log), [second run](samples/qwen2.5-0.5b-int8/x86_64_sub240_run2.log) |
| Qwen2.5-7B 8-bit | W512 | 512 | `18bc03ff693322bba5bd0f6969dc0291077aced5683602ff2604849fbdf55302` | [x86_64.log](samples/qwen2.5-7b-int8/x86_64.log), [second run](samples/qwen2.5-7b-int8/x86_64_run2.log) |
| Qwen2.5-7B 8-bit | W512, first 64 | 64 | `a606b312752c6c3bfbd21e96513abe36fc09bdda671d4d82fdc396125a620b98` | [x86_64_first64.log](samples/qwen2.5-7b-int8/x86_64_first64.log) |
| Qwen2.5-7B 4-bit (g) | W512 | 512 | `cf10ae9c81731610ad975c49852cbaa82ad61fdf94fd9cf3b1180700bef8c22d` | [x86_64.log](samples/qwen2.5-7b-int4-g/x86_64.log), [second run](samples/qwen2.5-7b-int4-g/x86_64_run2.log) |
| Qwen2.5-7B 4-bit (g) | W512, first 128 (W128) | 128 | `9320ecc5db7a3661f179672c7c156c9e1267afc997a873916b7fed293f747d01` | [x86_64_first128.log](samples/qwen2.5-7b-int4-g/x86_64_first128.log) |
| Qwen2.5-7B 4-bit (h) | W64 | 64 | `084adba34ef1f010593ec5e107f5ecdcd33c14e66fed324b1fc441d1a86c4a5e` | [x86_64.log](samples/qwen2.5-7b-4bit-h/x86_64.log) |

Each "second run" is an independent run with a different thread count and
has the same `CHAIN`. The first-64 and first-128 logs match the W512 logs
line by line (`compare --subset`).

A device whose log is re-issued for one of these workloads must give the
`CHAIN` shown here (for the same positions in the same order).

### GPU and phone logs in format v2

Every NVIDIA GPU log and the Galaxy Z Fold5 CPU logs published earlier have
been re-run and re-issued in format v2: 111 logs (37 single-stream GPU logs,
69 batched GPU logs and 5 Galaxy Z Fold5 logs). Each one's `CHAIN` (and the
`STREAMS` digest of batched logs) is in [samples/HASHES.tsv](samples/HASHES.tsv);
[samples/PAIRS.tsv](samples/PAIRS.tsv) lists the 109 pairs that must match.
For each re-run, the earlier-format chain digest of the same run equals
the previously published one.

| Family | GPUs / devices | Logs | `CHAIN` (stream 0 for batched logs) |
|---|---|---|---|
| Qwen2.5-0.5B 8-bit, W3260 | NVIDIA T4; Galaxy Z Fold5 CPU | 2 | `7fee20db…f065` (same as x86-64 CPU) |
| Qwen2.5-0.5B 8-bit, W240 | Galaxy Z Fold5 CPU | 1 | `224cc35a…0027` (same as x86-64 CPU) |
| Qwen2.5-7B 8-bit, W512 | NVIDIA A10 | 1 | `18bc03ff…5302` (same as x86-64 CPU) |
| Qwen2.5-7B 4-bit (g), W512 | NVIDIA A10 | 1 | `cf10ae9c…c22d` (same as x86-64 CPU) |
| Qwen2.5-7B 4-bit (g), first 128 | Galaxy Z Fold5 CPU, 3 runs | 3 | `9320ecc5…7d01` (same as x86-64 CPU) |
| Qwen2.5-7B 4-bit (g), batched B = 1–64 | NVIDIA A10G, A10 | 40 | every row of every stream matches the x86-64 CPU log |
| Qwen2.5-7B 4-bit (h), W64 | NVIDIA H100, H200, A100, B200, L4, RTX PRO 6000, GeForce RTX 3090, RTX 4090, RTX 5090 | 9 | `084adba3…4a5e` (same as x86-64 CPU) |
| Qwen2.5-7B 4-bit (h), batched B = 8–128 | NVIDIA H100, H200, A100, B200, L4, RTX PRO 6000, GeForce RTX 4090, RTX 5090 | 29 | every row of every stream matches the x86-64 CPU log |
| Qwen2.5-7B 4-bit (h), 256 generations | NVIDIA A10, L40S, A100, H100, H200, RTX PRO 6000, L4, B200 | 8 | one `CHAIN` for all eight |
| Idemcore 27B, 3 test sets | NVIDIA A100, H200, GeForce RTX 3090, RTX 5090 | 12 | one `CHAIN` per test set, equal on all four GPUs |
| Idemcore 35B (MoE), 3 test sets | NVIDIA A100 | 3 | published; no second device in format v2 yet |
| gpt-oss-20b (MoE), W512 | x86-64 CPU, NVIDIA L40S | 2 | published; same `CHAIN` on both |
| gpt-oss-120b (MoE), W512 | x86-64 CPU, NVIDIA H100 | 2 | published; same `CHAIN` on both |

The Snapdragon judge kit on <https://idemcore.net/verify/snapdragon> carries
the format v2 logs of the 0.5B and 7B Snapdragon GPU runs (Galaxy Z Fold5,
Adreno 740) and of the 0.5B run on NVIDIA A100, H100, L4 and RTX PRO 6000.

### Re-issued 2026-11-21

| Run | Logs | Status |
|---|---|---|
| gpt-oss-20b (MoE) W512, x86-64 CPU, 8 threads | [x86_64.log](samples/gpt-oss-20b/x86_64.log) | published; same `CHAIN` as NVIDIA L40S |
| gpt-oss-120b (MoE) W512, x86-64 CPU, 16 cores | [x86_64.log](samples/gpt-oss-120b/x86_64.log) | published; same `CHAIN` as NVIDIA H100, all 512 positions |
| Qwen2.5-0.5B 8-bit, Galaxy Z Fold5 Hexagon NPU, W240 and W3260 | [W240](samples/qwen2.5-0.5b-int8/android_fold5_hexagon_npu_sub240.log), [W3260](samples/qwen2.5-0.5b-int8/android_fold5_hexagon_npu.log) | published; same `CHAIN` as x86-64 CPU (`224cc35a…0027`, `7fee20db…f065`) |
| Qwen2.5-7B 8-bit, Galaxy Z Fold5 CPU, first 64 | [android_fold5_first64.log](samples/qwen2.5-7b-int8/android_fold5_first64.log) | published |
| Windows 11 ARM64 laptop (Snapdragon X Plus): CPU 0.5B W240; Adreno X1-85 GPU 0.5B W240 and W3260, 7B 4-bit (g) first 128 | [CPU W240](samples/qwen2.5-0.5b-int8/windows_arm64_cpu_sub240.log), [GPU W240](samples/qwen2.5-0.5b-int8/windows_arm64_adreno_x1_85_sub240.log), [GPU W3260](samples/qwen2.5-0.5b-int8/windows_arm64_adreno_x1_85.log), [GPU 7B first 128](samples/qwen2.5-7b-int4-g/windows_arm64_adreno_x1_85_first128.log) | published; written by the fixed logger with LF line endings. The earlier files with Windows line endings fail the check and are not published or edited |

### Not yet re-issued

| Run | Status |
|---|---|
| x86-64 CPU repeat runs of Qwen2.5-7B 4-bit (g) (3 × 8 threads, 3 × 6 threads) | replaced by the independent second run above |

Qwen2.5-7B 4-bit (g4) is withdrawn from the published evidence: its model
file is no longer available, so it cannot be re-issued in format v2.
Until a run is re-issued, its result stays documented in
[RESULTS.md](RESULTS.md) but cannot be checked with this verifier.
