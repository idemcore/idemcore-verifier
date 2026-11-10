# Sample logs

All logs are raw output of real runs, unedited except whitespace
normalisation, removal of lines that format v1 does not use, and (since
0.3.2) conversion to the hash-only form of [SPEC.md](../SPEC.md): each token
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
| qwen2.5-7b-int4-g/android_fold5_first128_pathA.log | same | Galaxy Z Fold5, 4 big cores, repeat run 1, 2026-10-30 | 128 (payload 0, positions 0–127) | 8d694e5c633851cc |
| qwen2.5-7b-int4-g/android_fold5_first128_pathB.log | same | Galaxy Z Fold5, 4 big cores, repeat run 2, 2026-10-30 | 128 (payload 0, positions 0–127) | 8d694e5c633851cc |
| qwen2.5-7b-int4-g/x86_64_repeat/t{8,6}_run{1,2,3}.log | same | x86-64, 8 or 6 pinned threads, 3 repeat runs each | 512 | a921e042378ae5a7 |
| qwen2.5-7b-int4-g4/x86_64.log | Qwen2.5-7B-Instruct, 4-bit variant g4 | x86-64 | 512 | 4765031d077c0202 |
| qwen2.5-7b-int4-g4/nvidia_a10g.log | same | NVIDIA A10G (sm_86) | 512 | 4765031d077c0202 |
| gpt-oss-20b/x86_64.log | gpt-oss-20b (MoE) | x86-64 cloud CPU, 16 threads | 512 | 8ec348aaf3b4109c |
| gpt-oss-20b/nvidia_l40s.log | same | NVIDIA L40S (sm_89) | 512 | 8ec348aaf3b4109c |
| gpt-oss-120b/x86_64_first4x32.log | gpt-oss-120b (MoE) | x86-64 cloud CPU, 16 threads | 128 (4 × first 32) | 95b6e5a6f0a2f1e7 |
| gpt-oss-120b/nvidia_h100.log | same | NVIDIA H100 80GB (sm_90) | 512 | 024c898ae3cff89e |
| qwen2.5-0.5b-int8/android_fold5.log | Qwen2.5-0.5B-Instruct, 8-bit | Samsung Galaxy Z Fold5 SM-F946B, Snapdragon 8 Gen 2, Android 16, 4 threads, 2026-10-29 | 3260 | 5cd062ce79583b61 |
| qwen2.5-7b-4bit-h/nvidia_h100.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA H100 80GB (reference), 2026-10-31 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA RTX PRO 6000 Blackwell 96GB, 2026-11-04 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_rtx_4090.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA GeForce RTX 4090 24GB, 2026-11-04 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_rtx_3090.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA GeForce RTX 3090 24GB, 2026-11 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_rtx_5090.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA GeForce RTX 5090 32GB, 2026-11 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_a100.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA A100 80GB, 2026-11-05 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_h200.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA H200 141GB, 2026-11-05 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_l4.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA L4 24GB, 2026-11-10 | 64 | 9560d1ac36828c79 |
| qwen2.5-7b-4bit-h/nvidia_b200.log | Qwen2.5-7B-Instruct, 4-bit variant h | NVIDIA B200 180GB, 2026-11-10 | 64 | 9560d1ac36828c79 |
| idemcore-27b/nvidia_a100_short.log | Idemcore 27B, test set short | NVIDIA A100 80GB, 2026-11-05 | 512 | 83893c53bcbf5cea |
| idemcore-27b/nvidia_a100_eval.log | Idemcore 27B, test set eval | NVIDIA A100 80GB, 2026-11-05 | 2560 | 047de5e4e45b799d |
| idemcore-27b/nvidia_a100_dec.log | Idemcore 27B, test set dec | NVIDIA A100 80GB, 2026-11-05 | 2048 | b5e75b4bb36de82b |
| idemcore-27b/nvidia_h200_short.log | Idemcore 27B, test set short | NVIDIA H200 141GB, 2026-11-05 | 512 | 83893c53bcbf5cea |
| idemcore-27b/nvidia_h200_eval.log | Idemcore 27B, test set eval | NVIDIA H200 141GB, 2026-11-05 | 2560 | 047de5e4e45b799d |
| idemcore-27b/nvidia_h200_dec.log | Idemcore 27B, test set dec | NVIDIA H200 141GB, 2026-11-05 | 2048 | b5e75b4bb36de82b |
| idemcore-27b/nvidia_rtx_3090_short.log | Idemcore 27B, test set short | NVIDIA GeForce RTX 3090 24GB, 2026-11 | 512 | 83893c53bcbf5cea |
| idemcore-27b/nvidia_rtx_3090_eval.log | Idemcore 27B, test set eval | NVIDIA GeForce RTX 3090 24GB, 2026-11 | 2560 | 047de5e4e45b799d |
| idemcore-27b/nvidia_rtx_3090_dec.log | Idemcore 27B, test set dec | NVIDIA GeForce RTX 3090 24GB, 2026-11 | 2048 | b5e75b4bb36de82b |
| idemcore-27b/nvidia_rtx_5090_short.log | Idemcore 27B, test set short | NVIDIA GeForce RTX 5090 32GB, 2026-11 | 512 | 83893c53bcbf5cea |
| idemcore-27b/nvidia_rtx_5090_eval.log | Idemcore 27B, test set eval | NVIDIA GeForce RTX 5090 32GB, 2026-11 | 2560 | 047de5e4e45b799d |
| idemcore-27b/nvidia_rtx_5090_dec.log | Idemcore 27B, test set dec | NVIDIA GeForce RTX 5090 32GB, 2026-11 | 2048 | b5e75b4bb36de82b |
| idemcore-35b-moe/nvidia_a100_short.log | Idemcore 35B (MoE), test set short | NVIDIA A100 80GB, 2026-11-05 | 512 | af3e1f4abc44d136 |
| idemcore-35b-moe/nvidia_a100_eval.log | Idemcore 35B (MoE), test set eval | NVIDIA A100 80GB, 2026-11-05 | 2560 | 3e2948d2deaadc71 |
| idemcore-35b-moe/nvidia_a100_dec.log | Idemcore 35B (MoE), test set dec | NVIDIA A100 80GB, 2026-11-05 | 2048 | 87953767681c3354 |

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

## Qwen2.5-7B 4-bit (h) across nine NVIDIA GPUs

`qwen2.5-7b-4bit-h/<gpu>.log`: one stream, 64 teacher-forced positions, hash-only form.
Every file has `ALL 9560d1ac36828c79`, and PAIRS.tsv compares each GPU with the H100 log position by position.

`batched/qwen2.5-7b-4bit-h/<gpu>/s64_b{8,32,64,128}.log.gz`: `B` concurrent streams of 64 positions each (stream `s` carries its own token sequence; stream 0 is the single-stream workload).
For each `B`, every GPU gives the same `ALL[0]` and the same `STREAMS` digest (see HASHES.tsv), so every stream's chain is identical across GPUs.
Batch sizes per GPU: H100, H200, A100, RTX PRO 6000, B200: 8/32/64/128; RTX 4090, RTX 5090, L4: 8/32/64; RTX 3090: single stream (no batched logs).

These logs were converted from the original run output to the hash-only form: only the per-token hash fields and the `ALL` lines were kept.


## Qwen2.5-7B 4-bit (h), 256 generations

`qwen2.5-7b-4bit-h-seeded/<gpu>.log`: 256 generations (64 prompts × 4 seeds
1001, 1002, 1003, 1004), temperature 0.7, top-k 50, top-p 0.90, 128 new
tokens each, hash-only form. Every file has `ALL 8774afd4535d0cb7`.
Each log also includes the checked prompt positions; prompts differ in length, so each generation has 144–151 rows and each file has 37,800 rows.
PAIRS.tsv compares each GPU with the NVIDIA A10 log
position by position.

| File | Device | Date (Asia/Saigon, UTC+7) | Positions | ALL |
|---|---|---|---|---|
| qwen2.5-7b-4bit-h-seeded/nvidia_a10.log | NVIDIA A10 (reference) | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_l40s.log | NVIDIA L40S | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_a100.log | NVIDIA A100 80GB | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_h100.log | NVIDIA H100 80GB | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_h200.log | NVIDIA H200 141GB | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_rtx_pro_6000.log | NVIDIA RTX PRO 6000 Blackwell 96GB | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_b200.log | NVIDIA B200 180GB | 2026-11-10 | 37800 | 8774afd4535d0cb7 |
| qwen2.5-7b-4bit-h-seeded/nvidia_l4.log | NVIDIA L4 24GB | 2026-11-11 | 37800 | 8774afd4535d0cb7 |

These logs were converted from the original run output to the hash-only form:
only the per-token hash fields and the `ALL` line were kept. NVIDIA T4 was
not run (this model is not supported on T4 in the engine used; a coverage
gap, not a failure). GeForce RTX 3090, 4090 and 5090 were not offered by
the machine pool used, so they were not run.

## Idemcore 27B and Idemcore 35B (MoE)

`idemcore-27b/<gpu>_{short,eval,dec}.log` and `idemcore-35b-moe/nvidia_a100_{short,eval,dec}.log`: same hash form as the logs above (`pi j h hc`, one line per position, then `ALL`), three fixed teacher-forced test sets per model:

* `short`: 4 sequences of 128 positions (512 rows).
* `eval`: 4 sequences of 128 positions plus 1 sequence of 2048 positions (2560 rows).
* `dec`: 32 sequences of 64 positions (2048 rows).

For each test set, the files from different GPUs are byte-identical, and each `ALL` equals the reference digest recorded on NVIDIA H100:
27B short `83893c53bcbf5cea`, eval `047de5e4e45b799d`, dec `b5e75b4bb36de82b`;
35B short `af3e1f4abc44d136`, eval `3e2948d2deaadc71`, dec `87953767681c3354`.
PAIRS.tsv compares the 27B logs of H200, RTX 3090 and RTX 5090 with the A100 log position by position.

Of the 35B runs, the A100 logs were kept. For the H100 reference runs of both models, and the 27B/35B runs on other GPUs, the digests are recorded but the raw logs are not published.
These files are the original run output; they already consisted of the hash fields and the `ALL` line, so nothing was removed.
