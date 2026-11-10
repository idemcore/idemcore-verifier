# Evidence pack

Every hash below is recomputed from the shipped logs by one command:

```sh
make verify            # or: python3 -m idemcore_verify samples
```

It reads [samples/HASHES.tsv](samples/HASHES.tsv) (the published digests) and [samples/PAIRS.tsv](samples/PAIRS.tsv) (which log must match which), recomputes every chained digest from the per-token lines, re-compares every pair, and prints `PASS` or `FAIL`. Standard library only; about 4 seconds on a laptop.

Workloads (teacher-forced, the same token files on every device):

| Workload | Positions | Expected `ALL` (Qwen2.5-7B 4-bit (g)) |
|---|---|---|
| W512 | 4 payloads × 128 positions | `a921e042378ae5a7` |
| W128 | payload 0, positions 0–127 (the phone workload) | `8d694e5c633851cc` |

## 1. Single-stream logs, by model and device

### Qwen2.5-0.5B 8-bit

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU (Intel Xeon VM) | W3260 | 3260 | `5cd062ce79583b61` | [x86_64.log](samples/qwen2.5-0.5b-int8/x86_64.log) |
| NVIDIA T4 | W3260 | 3260 | `5cd062ce79583b61` | [nvidia_t4.log](samples/qwen2.5-0.5b-int8/nvidia_t4.log) |
| x86-64 CPU | W240 | 240 | `86b78a45359fa0e2` | [x86_64_sub240.log](samples/qwen2.5-0.5b-int8/x86_64_sub240.log) |
| Galaxy Z Fold5, 1 thread | W240 | 240 | `86b78a45359fa0e2` | [android_fold5_sub240.log](samples/qwen2.5-0.5b-int8/android_fold5_sub240.log) |
| Windows 11 ARM64 (Snapdragon X Plus), 1 thread | W240 | 240 | `86b78a45359fa0e2` | [windows_arm64_snapdragon_x_sub240.log](samples/qwen2.5-0.5b-int8/windows_arm64_snapdragon_x_sub240.log) |

### Qwen2.5-7B 8-bit

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU, 8 threads | W512 | 512 | `99d2f1efe2135c18` | [x86_64.log](samples/qwen2.5-7b-int8/x86_64.log) |
| NVIDIA A10 | W512 | 512 | `99d2f1efe2135c18` | [nvidia_a10.log](samples/qwen2.5-7b-int8/nvidia_a10.log) |
| Galaxy Z Fold5, 4 threads | W64 | 64 | `92161a9755d5a296` | [android_fold5_first64.log](samples/qwen2.5-7b-int8/android_fold5_first64.log) |

### Qwen2.5-7B 4-bit (g)

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU, 8 threads | W512 | 512 | `a921e042378ae5a7` | [x86_64.log](samples/qwen2.5-7b-int4-g/x86_64.log) |
| x86-64 CPU, 8 pinned threads, repeat 1 | W512 | 512 | `a921e042378ae5a7` | [t8_run1.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t8_run1.log) |
| x86-64 CPU, 8 pinned threads, repeat 2 | W512 | 512 | `a921e042378ae5a7` | [t8_run2.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t8_run2.log) |
| x86-64 CPU, 8 pinned threads, repeat 3 | W512 | 512 | `a921e042378ae5a7` | [t8_run3.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t8_run3.log) |
| x86-64 CPU, 6 pinned threads, repeat 1 | W512 | 512 | `a921e042378ae5a7` | [t6_run1.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t6_run1.log) |
| x86-64 CPU, 6 pinned threads, repeat 2 | W512 | 512 | `a921e042378ae5a7` | [t6_run2.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t6_run2.log) |
| x86-64 CPU, 6 pinned threads, repeat 3 | W512 | 512 | `a921e042378ae5a7` | [t6_run3.log](samples/qwen2.5-7b-int4-g/x86_64_repeat/t6_run3.log) |
| NVIDIA A10 | W512 | 512 | `a921e042378ae5a7` | [nvidia_a10.log](samples/qwen2.5-7b-int4-g/nvidia_a10.log) |
| Galaxy Z Fold5, 4 big cores (first run) | W128 | 128 | `8d694e5c633851cc` | [android_fold5_first128.log](samples/qwen2.5-7b-int4-g/android_fold5_first128.log) |
| Galaxy Z Fold5, 4 big cores, repeat run 1 | W128 | 128 | `8d694e5c633851cc` | [android_fold5_first128_pathA.log](samples/qwen2.5-7b-int4-g/android_fold5_first128_pathA.log) |
| Galaxy Z Fold5, 4 big cores, repeat run 2 | W128 | 128 | `8d694e5c633851cc` | [android_fold5_first128_pathB.log](samples/qwen2.5-7b-int4-g/android_fold5_first128_pathB.log) |

### Qwen2.5-7B 4-bit (g4)

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU | W512 | 512 | `4765031d077c0202` | [x86_64.log](samples/qwen2.5-7b-int4-g4/x86_64.log) |
| NVIDIA A10G | W512 | 512 | `4765031d077c0202` | [nvidia_a10g.log](samples/qwen2.5-7b-int4-g4/nvidia_a10g.log) |

### gpt-oss-20b (MoE)

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU, 16 threads | W512 | 512 | `8ec348aaf3b4109c` | [x86_64.log](samples/gpt-oss-20b/x86_64.log) |
| NVIDIA L40S | W512 | 512 | `8ec348aaf3b4109c` | [nvidia_l40s.log](samples/gpt-oss-20b/nvidia_l40s.log) |

### gpt-oss-120b (MoE)

| Device | Workload | Positions | ALL | File |
|---|---|---|---|---|
| x86-64 CPU, 16 threads (spot check) | W4x32 | 128 | `95b6e5a6f0a2f1e7` | [x86_64_first4x32.log](samples/gpt-oss-120b/x86_64_first4x32.log) |
| NVIDIA H100 80GB | W512 | 512 | `024c898ae3cff89e` | [nvidia_h100.log](samples/gpt-oss-120b/nvidia_h100.log) |

Same workload ⇒ same `ALL`. Different workloads of one model (e.g. W512 vs W128) differ by design, because `ALL` chains only the lines present; those pairs are checked position by position (`subset` mode in PAIRS.tsv).

**Galaxy Z Fold5, Qwen2.5-7B 4-bit (g), 2026-10-30.** Two repeat runs on the Fold5 (files `_pathA` and `_pathB`) both produced the byte-identical log and `ALL 8d694e5c633851cc`, the same as x86-64 and both GPUs. Speed on 4 big cores: 2.98 tok/s and 2.78 tok/s in these runs (3.39 tok/s in the earlier run reported in RESULTS.md; phone speed varies with temperature and background load).

**x86-64 repeats.** Six further runs of W512 on one x86-64 machine (8 and 6 pinned threads, 3 runs each) all give `ALL a921e042378ae5a7`, the same as the reference log.

## 1b. Qwen2.5-7B 4-bit (h) on nine NVIDIA GPUs

Workload W64: one stream of 64 teacher-forced positions. Every GPU gives the same `ALL`, and each is compared position by position with the H100 log (PAIRS.tsv).

| GPU | Date | Positions | ALL | File | Batched logs (same `ALL[0]` and `STREAMS` on every GPU) |
|---|---|---|---|---|---|
| NVIDIA H100 80GB (reference) | 2026-10-31 | 64 | `9560d1ac36828c79` | [nvidia_h100.log](samples/qwen2.5-7b-4bit-h/nvidia_h100.log) | B=8, B=32, B=64, B=128 |
| NVIDIA RTX PRO 6000 Blackwell 96GB | 2026-11-04 | 64 | `9560d1ac36828c79` | [nvidia_rtx_pro_6000.log](samples/qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000.log) | B=8, B=32, B=64, B=128 |
| NVIDIA GeForce RTX 4090 24GB | 2026-11-04 | 64 | `9560d1ac36828c79` | [nvidia_rtx_4090.log](samples/qwen2.5-7b-4bit-h/nvidia_rtx_4090.log) | B=8, B=32, B=64 |
| NVIDIA GeForce RTX 3090 24GB | 2026-11 | 64 | `9560d1ac36828c79` | [nvidia_rtx_3090.log](samples/qwen2.5-7b-4bit-h/nvidia_rtx_3090.log) | — |
| NVIDIA GeForce RTX 5090 32GB | 2026-11 | 64 | `9560d1ac36828c79` | [nvidia_rtx_5090.log](samples/qwen2.5-7b-4bit-h/nvidia_rtx_5090.log) | B=8, B=32, B=64 |
| NVIDIA A100 80GB | 2026-11-05 | 64 | `9560d1ac36828c79` | [nvidia_a100.log](samples/qwen2.5-7b-4bit-h/nvidia_a100.log) | B=8, B=32, B=64, B=128 |
| NVIDIA H200 141GB | 2026-11-05 | 64 | `9560d1ac36828c79` | [nvidia_h200.log](samples/qwen2.5-7b-4bit-h/nvidia_h200.log) | B=8, B=32, B=64, B=128 |
| NVIDIA L4 24GB | 2026-11-10 | 64 | `9560d1ac36828c79` | [nvidia_l4.log](samples/qwen2.5-7b-4bit-h/nvidia_l4.log) | B=8, B=32, B=64 |
| NVIDIA B200 180GB | 2026-11-10 | 64 | `9560d1ac36828c79` | [nvidia_b200.log](samples/qwen2.5-7b-4bit-h/nvidia_b200.log) | B=8, B=32, B=64, B=128 |

`STREAMS` digests per batch size (identical on every GPU that ran it): B=8 `2bfd844f8132186b`, B=32 `941af9781d6891b8`, B=64 `1002404b022a3e80`, B=128 `d168d5a98d0f8a79`.

**Qwen2.5-0.5B 8-bit, full 3260-position run on the Galaxy Z Fold5 (2026-10-29, 4 threads):** `ALL 5cd062ce79583b61`, 3260/3260 positions identical to x86-64 and T4 ([android_fold5.log](samples/qwen2.5-0.5b-int8/android_fold5.log)). The Windows 11 ARM64 3260-position run is a written record only; its raw log was not kept, so only the 240-position log is published for that device.

## 1c. Idemcore 27B and Idemcore 35B (MoE)

Three fixed teacher-forced test sets per model: `short` (4 × 128 positions), `eval` (4 × 128 plus 1 × 2048) and `dec` (32 × 64), 5120 positions in total. For each test set, the logs from different GPUs are byte-identical and every `ALL` equals the reference digest recorded on NVIDIA H100. PAIRS.tsv compares the 27B logs of H200, RTX 3090 and RTX 5090 with the A100 log position by position.

| Model | Test set | Positions | ALL (= H100 reference) | Published logs |
|---|---|---|---|---|
| Idemcore 27B | short | 512 | `83893c53bcbf5cea` | A100, H200, RTX 3090, RTX 5090 ([samples/idemcore-27b/](samples/idemcore-27b/)) |
| Idemcore 27B | eval | 2560 | `047de5e4e45b799d` | A100, H200, RTX 3090, RTX 5090 |
| Idemcore 27B | dec | 2048 | `b5e75b4bb36de82b` | A100, H200, RTX 3090, RTX 5090 |
| Idemcore 35B (MoE) | short | 512 | `af3e1f4abc44d136` | A100 ([samples/idemcore-35b-moe/](samples/idemcore-35b-moe/)) |
| Idemcore 35B (MoE) | eval | 2560 | `3e2948d2deaadc71` | A100 |
| Idemcore 35B (MoE) | dec | 2048 | `87953767681c3354` | A100 |

For the H100 reference runs and the 27B/35B runs on other GPUs, the digests are recorded but the raw logs are not published.

## 2. Batched GPU logs (Qwen2.5-7B 4-bit (g))

Format: [SPEC.md § Batched logs](SPEC.md#batched-logs). One file holds `B` concurrent streams. `ALL[0]` is stream 0's chained digest; `STREAMS` is a digest over every stream's `ALL` (it changes if any stream changes). Every row of every stream (including warm-up filler slots of staggered runs) is also compared against the single-stream x86-64 log by `(payload, position)`; all rows match.

### NVIDIA A10G

| Workload | B | Schedule | Rows compared | ALL[0] | STREAMS | Aggregate tok/s | File |
|---|---|---|---|---|---|---|---|
| W512 | 1 | in order | 512 | `a921e042378ae5a7` | `a947839ae8d342f6` | 92.69 | [w512_b1.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b1.log.gz) |
| W512 | 8 | in order | 4096 | `a921e042378ae5a7` | `2828ba1f6d95db01` | 641.37 | [w512_b8.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b8.log.gz) |
| W512 | 16 | in order | 8192 | `a921e042378ae5a7` | `adf245b7df2665c4` | 1057.55 | [w512_b16.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16.log.gz) |
| W512 | 32 | in order | 16384 | `a921e042378ae5a7` | `bbadca559405cb60` | 1371.69 | [w512_b32.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32.log.gz) |
| W512 | 64 | in order | 32768 | `a921e042378ae5a7` | `9ea9c265503d1a40` | 1413.34 | [w512_b64.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64.log.gz) |
| W512 | 16 | shuffled slots | 8192 | `a921e042378ae5a7` | `adf245b7df2665c4` |  | [w512_b16_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16_shuffled.log.gz) |
| W512 | 32 | shuffled slots | 16384 | `a921e042378ae5a7` | `bbadca559405cb60` |  | [w512_b32_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32_shuffled.log.gz) |
| W512 | 64 | shuffled slots | 32768 | `a921e042378ae5a7` | `9ea9c265503d1a40` |  | [w512_b64_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64_shuffled.log.gz) |
| W512 | 16 | staggered joins | 8192 | `a921e042378ae5a7` | `4f619a3bedff14af` |  | [w512_b16_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16_staggered.log.gz) |
| W512 | 32 | staggered joins | 16384 | `a921e042378ae5a7` | `c17249fc5eb5a77f` |  | [w512_b32_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32_staggered.log.gz) |
| W512 | 64 | staggered joins | 32768 | `a921e042378ae5a7` | `053e6f9df9d0e848` |  | [w512_b64_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64_staggered.log.gz) |
| W128 | 1 | in order | 128 | `8d694e5c633851cc` | `da7752b1247bbff7` |  | [w128_b1.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b1.log.gz) |
| W128 | 8 | in order | 1024 | `8d694e5c633851cc` | `89e358a3bac09fe9` |  | [w128_b8.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b8.log.gz) |
| W128 | 16 | in order | 2048 | `8d694e5c633851cc` | `d590bd3506523693` |  | [w128_b16.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b16.log.gz) |
| W128 | 32 | in order | 4096 | `8d694e5c633851cc` | `763c1665de4e5198` |  | [w128_b32.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32.log.gz) |
| W128 | 64 | in order | 8192 | `8d694e5c633851cc` | `9a241b64b19d222e` |  | [w128_b64.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64.log.gz) |
| W128 | 32 | shuffled slots | 4096 | `8d694e5c633851cc` | `763c1665de4e5198` |  | [w128_b32_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32_shuffled.log.gz) |
| W128 | 64 | shuffled slots | 8192 | `8d694e5c633851cc` | `9a241b64b19d222e` |  | [w128_b64_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64_shuffled.log.gz) |
| W128 | 32 | staggered joins | 4096 | `8d694e5c633851cc` | `535aa115282d7598` |  | [w128_b32_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32_staggered.log.gz) |
| W128 | 64 | staggered joins | 8192 | `8d694e5c633851cc` | `112f81d4bc97c1d0` |  | [w128_b64_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64_staggered.log.gz) |

### NVIDIA A10

| Workload | B | Schedule | Rows compared | ALL[0] | STREAMS | Aggregate tok/s | File |
|---|---|---|---|---|---|---|---|
| W512 | 1 | in order | 512 | `a921e042378ae5a7` | `a947839ae8d342f6` | 92.44 | [w512_b1.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b1.log.gz) |
| W512 | 8 | in order | 4096 | `a921e042378ae5a7` | `2828ba1f6d95db01` | 616.29 | [w512_b8.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b8.log.gz) |
| W512 | 16 | in order | 8192 | `a921e042378ae5a7` | `adf245b7df2665c4` | 956.26 | [w512_b16.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16.log.gz) |
| W512 | 32 | in order | 16384 | `a921e042378ae5a7` | `bbadca559405cb60` | 1325.40 | [w512_b32.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32.log.gz) |
| W512 | 64 | in order | 32768 | `a921e042378ae5a7` | `9ea9c265503d1a40` | 1259.07 | [w512_b64.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64.log.gz) |
| W512 | 16 | shuffled slots | 8192 | `a921e042378ae5a7` | `adf245b7df2665c4` |  | [w512_b16_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16_shuffled.log.gz) |
| W512 | 32 | shuffled slots | 16384 | `a921e042378ae5a7` | `bbadca559405cb60` |  | [w512_b32_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32_shuffled.log.gz) |
| W512 | 64 | shuffled slots | 32768 | `a921e042378ae5a7` | `9ea9c265503d1a40` |  | [w512_b64_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64_shuffled.log.gz) |
| W512 | 16 | staggered joins | 8192 | `a921e042378ae5a7` | `4f619a3bedff14af` |  | [w512_b16_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16_staggered.log.gz) |
| W512 | 32 | staggered joins | 16384 | `a921e042378ae5a7` | `c17249fc5eb5a77f` |  | [w512_b32_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32_staggered.log.gz) |
| W512 | 64 | staggered joins | 32768 | `a921e042378ae5a7` | `053e6f9df9d0e848` |  | [w512_b64_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64_staggered.log.gz) |
| W128 | 1 | in order | 128 | `8d694e5c633851cc` | `da7752b1247bbff7` |  | [w128_b1.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b1.log.gz) |
| W128 | 8 | in order | 1024 | `8d694e5c633851cc` | `89e358a3bac09fe9` |  | [w128_b8.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b8.log.gz) |
| W128 | 16 | in order | 2048 | `8d694e5c633851cc` | `d590bd3506523693` |  | [w128_b16.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b16.log.gz) |
| W128 | 32 | in order | 4096 | `8d694e5c633851cc` | `763c1665de4e5198` |  | [w128_b32.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32.log.gz) |
| W128 | 64 | in order | 8192 | `8d694e5c633851cc` | `9a241b64b19d222e` |  | [w128_b64.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64.log.gz) |
| W128 | 32 | shuffled slots | 4096 | `8d694e5c633851cc` | `763c1665de4e5198` |  | [w128_b32_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32_shuffled.log.gz) |
| W128 | 64 | shuffled slots | 8192 | `8d694e5c633851cc` | `9a241b64b19d222e` |  | [w128_b64_shuffled.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64_shuffled.log.gz) |
| W128 | 32 | staggered joins | 4096 | `8d694e5c633851cc` | `535aa115282d7598` |  | [w128_b32_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32_staggered.log.gz) |
| W128 | 64 | staggered joins | 8192 | `8d694e5c633851cc` | `112f81d4bc97c1d0` |  | [w128_b64_staggered.log.gz](samples/batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64_staggered.log.gz) |

The `STREAMS` digests are equal on A10G and A10 for every configuration, and equal between in-order and shuffled-slot runs of the same `B` (shuffling changes which slot serves which stream, not which stream gets which tokens). Staggered runs have a different `STREAMS` digest only because their stream set and stream contents differ by design; each of their rows still matches x86-64.

Throughput is for W512 in slot order, teacher-forced GPU step time (see [RESULTS.md §2b](RESULTS.md#2b-batched-serving-qwen25-7b-4-bit-g-nvidia-a10g) for caveats and the vLLM comparison). A10G at 1710 MHz SM; A10 from the same cloud pool.

### NVIDIA H100

TODO: batched Qwen2.5-7B 4-bit (g) run on H100 (B = 1–64, shuffled, staggered). Not run yet. H100 batched logs for Qwen2.5-7B 4-bit (h) are in section 1b.

## 3. Cross-device summary (Qwen2.5-7B 4-bit (g))

| Device | Mode | W128 `ALL` / stream 0 | W512 `ALL` / stream 0 |
|---|---|---|---|
| x86-64 CPU (7 runs) | single stream | via subset compare | `a921e042378ae5a7` |
| Galaxy Z Fold5 (3 runs) | single stream | `8d694e5c633851cc` | — (phone runs W128 only) |
| NVIDIA A10 | single stream | — | `a921e042378ae5a7` |
| NVIDIA A10 | batched, B=1–64 | `8d694e5c633851cc` | `a921e042378ae5a7` |
| NVIDIA A10G | batched, B=1–64 | `8d694e5c633851cc` | `a921e042378ae5a7` |
| NVIDIA H100 | batched | TODO | TODO |

## How to add a result

See [CONTRIBUTING.md](CONTRIBUTING.md). Add the log under `samples/`, a row to `HASHES.tsv`, a pair to `PAIRS.tsv`, and run `make verify`.
