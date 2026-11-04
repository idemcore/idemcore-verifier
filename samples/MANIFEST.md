# Sample logs

All logs are raw output of real runs, unedited except whitespace
normalisation, removal of lines that format v1 does not use, and (since
0.3.2) reduction to the hash-only form of [SPEC.md](../SPEC.md): each token
line keeps `pi j h hc` (batched: `s pi j h hc`). `ALL` and `STREAMS` depend
only on `h` and `hc`, so every published digest is unchanged. Recompute any `ALL` with `python3 -m idemcore_verify check`.

| File | Model | Device | Positions | ALL |
|---|---|---|---|---|
| qwen2.5-0.5b-int8/x86_64.log | Qwen2.5-0.5B-Instruct, 8-bit | x86-64 (Intel Xeon VM) | 3260 | 5cd062ce79583b61 |
| qwen2.5-0.5b-int8/nvidia_t4.log | same | NVIDIA T4 (sm_75) | 3260 | 5cd062ce79583b61 |
| qwen2.5-0.5b-int8/x86_64_sub240.log | same | x86-64 | 240 | 86b78a45359fa0e2 |
| qwen2.5-0.5b-int8/android_fold5_sub240.log | same | Samsung Galaxy Z Fold5 SM-F946B, Snapdragon 8 Gen 2 (SM8550), Android 16, 1 thread | 240 | 86b78a45359fa0e2 |
| qwen2.5-0.5b-int8/windows_arm64_snapdragon_x_sub240.log | same | Windows 11 ARM64 laptop, Snapdragon X Plus (X1P64100), 1 thread | 240 | 86b78a45359fa0e2 |
| qwen2.5-7b-int8/x86_64.log | Qwen2.5-7B-Instruct, 8-bit | x86-64, 8 threads | 512 | 99d2f1efe2135c18 |
| qwen2.5-7b-int8/nvidia_a10.log | same | NVIDIA A10 (sm_86) | 512 | 99d2f1efe2135c18 |
| qwen2.5-7b-int8/android_fold5_first64.log | same | Galaxy Z Fold5, 4 threads | 64 (payload 0, positions 0–63) | 92161a9755d5a296 |
| qwen2.5-7b-int4-g/x86_64.log | Qwen2.5-7B-Instruct, 4-bit variant g | x86-64 | 512 | a921e042378ae5a7 |
| qwen2.5-7b-int4-g/nvidia_a10.log | same | NVIDIA A10 | 512 | a921e042378ae5a7 |
| qwen2.5-7b-int4-g/android_fold5_first128.log | same | Samsung Galaxy Z Fold5 SM-F946B, Snapdragon 8 Gen 2, Android 16, 4 big cores | 128 (payload 0, positions 0–127) | 8d694e5c633851cc |
| qwen2.5-7b-int4-g/android_fold5_first128_pathA.log | same | Galaxy Z Fold5, 4 big cores, CPU path A (default), 2026-10-30 | 128 (payload 0, positions 0–127) | 8d694e5c633851cc |
| qwen2.5-7b-int4-g/android_fold5_first128_pathB.log | same | Galaxy Z Fold5, 4 big cores, CPU path B (compatibility), 2026-10-30 | 128 (payload 0, positions 0–127) | 8d694e5c633851cc |
| qwen2.5-7b-int4-g/x86_64_repeat/t{8,6}_run{1,2,3}.log | same | x86-64, 8 or 6 pinned threads, 3 repeat runs each | 512 | a921e042378ae5a7 |
| qwen2.5-7b-int4-g4/x86_64.log | Qwen2.5-7B-Instruct, 4-bit variant g4 | x86-64 | 512 | 4765031d077c0202 |
| qwen2.5-7b-int4-g4/nvidia_a10g.log | same | NVIDIA A10G (sm_86) | 512 | 4765031d077c0202 |
| gpt-oss-20b/x86_64.log | gpt-oss-20b (MoE) | x86-64 cloud CPU, 16 threads | 512 | 8ec348aaf3b4109c |
| gpt-oss-20b/nvidia_l40s.log | same | NVIDIA L40S (sm_89) | 512 | 8ec348aaf3b4109c |
| gpt-oss-120b/x86_64_first4x32.log | gpt-oss-120b (MoE) | x86-64 cloud CPU, 16 threads | 128 (4 × first 32) | 95b6e5a6f0a2f1e7 |
| gpt-oss-120b/nvidia_h100.log | same | NVIDIA H100 80GB (sm_90) | 512 | 024c898ae3cff89e |

`ALL` differs between a full log and a subset log by design (it chains the
lines present). Subset pairs are checked position by position.


## Batched GPU logs

`batched/qwen2.5-7b-int4-g/{nvidia_a10g,nvidia_a10}/`: 20 files per GPU,
gzipped, format in [SPEC.md § Batched logs](../SPEC.md#batched-logs).

* `w512_b{1,8,16,32,64}.log.gz`: W512 workload, `B` streams in slot order.
* `w512_b{16,32,64}_{shuffled,staggered}.log.gz`: shuffled slot order;
  streams joining at staggered times into reused slots.
* `w128_b{1,8,16,32,64}.log.gz`, `w128_b{32,64}_{shuffled,staggered}.log.gz`:
  the 128-position phone workload.

Expected `ALL[0]` and `STREAMS` digests for every file: [HASHES.tsv](HASHES.tsv).
Logs were reduced to the lines defined by the format (token and `ALL` lines).
