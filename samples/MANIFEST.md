# Sample logs (format v2)

All files are format v2 (`FORMAT idemcore-log/v2`, SHA-256). Per-file
`CHAIN` values: [HASHES.tsv](HASHES.tsv). Pairs that must match:
[PAIRS.tsv](PAIRS.tsv). Re-issue status of earlier runs:
[../EVIDENCE.md](../EVIDENCE.md). Batched logs are gzip-compressed (`.log.gz`);
the verifier reads them directly.

| File | Kind | Model | Workload | Device | Batch | Schedule | Rows |
|---|---|---|---|---|---|---|---|
| qwen2.5-0.5b-int8/x86_64.log | single | Qwen2.5-0.5B 8-bit | W3260 | x86-64 CPU, 8 threads | 1 | - | 3260 |
| qwen2.5-0.5b-int8/x86_64_run2.log | single | Qwen2.5-0.5B 8-bit | W3260 | x86-64 CPU, 4 threads, second run | 1 | - | 3260 |
| qwen2.5-0.5b-int8/x86_64_sub240.log | single | Qwen2.5-0.5B 8-bit | W240 | x86-64 CPU, 8 threads | 1 | - | 240 |
| qwen2.5-0.5b-int8/x86_64_sub240_run2.log | single | Qwen2.5-0.5B 8-bit | W240 | x86-64 CPU, 1 thread, second run | 1 | - | 240 |
| qwen2.5-7b-int8/x86_64.log | single | Qwen2.5-7B 8-bit | W512 | x86-64 CPU, 8 threads | 1 | - | 512 |
| qwen2.5-7b-int8/x86_64_run2.log | single | Qwen2.5-7B 8-bit | W512 | x86-64 CPU, 6 threads, second run | 1 | - | 512 |
| qwen2.5-7b-int8/x86_64_first64.log | single | Qwen2.5-7B 8-bit | W512 first 64 | x86-64 CPU, 8 threads | 1 | - | 64 |
| qwen2.5-7b-int4-g/x86_64.log | single | Qwen2.5-7B 4-bit g | W512 | x86-64 CPU, 8 threads | 1 | - | 512 |
| qwen2.5-7b-int4-g/x86_64_run2.log | single | Qwen2.5-7B 4-bit g | W512 | x86-64 CPU, 6 threads, second run | 1 | - | 512 |
| qwen2.5-7b-int4-g/x86_64_first128.log | single | Qwen2.5-7B 4-bit g | W512 first 128 | x86-64 CPU, 8 threads | 1 | - | 128 |
| qwen2.5-7b-4bit-h/x86_64.log | single | Qwen2.5-7B 4-bit h | W64 | x86-64 CPU, 8 threads | 1 | - | 64 |
| gpt-oss-120b/nvidia_h100.log | single | gpt-oss-120b (MoE) | W512 | NVIDIA H100 80GB | 1 | - | 512 |
| gpt-oss-20b/nvidia_l40s.log | single | gpt-oss-20b (MoE) | W512 | NVIDIA L40S | 1 | - | 512 |
| idemcore-27b/nvidia_a100_dec.log | single | Idemcore 27B | D32x64 | NVIDIA A100 80GB | 1 | - | 2048 |
| idemcore-27b/nvidia_a100_eval.log | single | Idemcore 27B | E4x128+1x2048 | NVIDIA A100 80GB | 1 | - | 2560 |
| idemcore-27b/nvidia_a100_short.log | single | Idemcore 27B | S4x128 | NVIDIA A100 80GB | 1 | - | 512 |
| idemcore-27b/nvidia_h200_dec.log | single | Idemcore 27B | D32x64 | NVIDIA H200 141GB | 1 | - | 2048 |
| idemcore-27b/nvidia_h200_eval.log | single | Idemcore 27B | E4x128+1x2048 | NVIDIA H200 141GB | 1 | - | 2560 |
| idemcore-27b/nvidia_h200_short.log | single | Idemcore 27B | S4x128 | NVIDIA H200 141GB | 1 | - | 512 |
| idemcore-27b/nvidia_rtx_3090_dec.log | single | Idemcore 27B | D32x64 | NVIDIA GeForce RTX 3090 24GB | 1 | - | 2048 |
| idemcore-27b/nvidia_rtx_3090_eval.log | single | Idemcore 27B | E4x128+1x2048 | NVIDIA GeForce RTX 3090 24GB | 1 | - | 2560 |
| idemcore-27b/nvidia_rtx_3090_short.log | single | Idemcore 27B | S4x128 | NVIDIA GeForce RTX 3090 24GB | 1 | - | 512 |
| idemcore-27b/nvidia_rtx_5090_dec.log | single | Idemcore 27B | D32x64 | NVIDIA GeForce RTX 5090 32GB | 1 | - | 2048 |
| idemcore-27b/nvidia_rtx_5090_eval.log | single | Idemcore 27B | E4x128+1x2048 | NVIDIA GeForce RTX 5090 32GB | 1 | - | 2560 |
| idemcore-27b/nvidia_rtx_5090_short.log | single | Idemcore 27B | S4x128 | NVIDIA GeForce RTX 5090 32GB | 1 | - | 512 |
| idemcore-35b-moe/nvidia_a100_dec.log | single | Idemcore 35B (MoE) | D32x64 | NVIDIA A100 80GB | 1 | - | 2048 |
| idemcore-35b-moe/nvidia_a100_eval.log | single | Idemcore 35B (MoE) | E4x128+1x2048 | NVIDIA A100 80GB | 1 | - | 2560 |
| idemcore-35b-moe/nvidia_a100_short.log | single | Idemcore 35B (MoE) | S4x128 | NVIDIA A100 80GB | 1 | - | 512 |
| qwen2.5-0.5b-int8/android_fold5.log | single | Qwen2.5-0.5B 8-bit | W3260 | Galaxy Z Fold5, 4 threads | 1 | - | 3260 |
| qwen2.5-0.5b-int8/android_fold5_sub240.log | single | Qwen2.5-0.5B 8-bit | W240 | Galaxy Z Fold5, 1 thread | 1 | - | 240 |
| qwen2.5-0.5b-int8/nvidia_t4.log | single | Qwen2.5-0.5B 8-bit | W3260 | NVIDIA T4 | 1 | - | 3260 |
| qwen2.5-7b-4bit-h-seeded/nvidia_a10.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA A10 | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_a100.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA A100 80GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_b200.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA B200 180GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_h100.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA H100 80GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_h200.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA H200 141GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_l4.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA L4 24GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_l40s.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA L40S | 1 | - | 37800 |
| qwen2.5-7b-4bit-h-seeded/nvidia_rtx_pro_6000.log | single | Qwen2.5-7B 4-bit (h) | W256gen | NVIDIA RTX PRO 6000 Blackwell 96GB | 1 | - | 37800 |
| qwen2.5-7b-4bit-h/nvidia_a100.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA A100 80GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_b200.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA B200 180GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_h100.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA H100 80GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_h200.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA H200 141GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_l4.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA L4 24GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_rtx_3090.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA GeForce RTX 3090 24GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_rtx_4090.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA GeForce RTX 4090 24GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_rtx_5090.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA GeForce RTX 5090 32GB | 1 | - | 64 |
| qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000.log | single | Qwen2.5-7B 4-bit (h) | W64 | NVIDIA RTX PRO 6000 Blackwell 96GB | 1 | - | 64 |
| qwen2.5-7b-int4-g/android_fold5_first128.log | single | Qwen2.5-7B 4-bit (g) | W128 | Galaxy Z Fold5, 4 big cores (first run) | 1 | - | 128 |
| qwen2.5-7b-int4-g/android_fold5_first128_pathA.log | single | Qwen2.5-7B 4-bit (g) | W128 | Galaxy Z Fold5, 4 big cores, repeat run 1 | 1 | - | 128 |
| qwen2.5-7b-int4-g/android_fold5_first128_pathB.log | single | Qwen2.5-7B 4-bit (g) | W128 | Galaxy Z Fold5, 4 big cores, repeat run 2 | 1 | - | 128 |
| qwen2.5-7b-int4-g/nvidia_a10.log | single | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 1 | - | 512 |
| qwen2.5-7b-int8/nvidia_a10.log | single | Qwen2.5-7B 8-bit | W512 | NVIDIA A10 | 1 | - | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_a100/s64_b128.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA A100 80GB | 128 | in order | 8192 |
| batched/qwen2.5-7b-4bit-h/nvidia_a100/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA A100 80GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_a100/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA A100 80GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_a100/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA A100 80GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_b200/s64_b128.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA B200 180GB | 128 | in order | 8192 |
| batched/qwen2.5-7b-4bit-h/nvidia_b200/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA B200 180GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_b200/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA B200 180GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_b200/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA B200 180GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_h100/s64_b128.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H100 80GB | 128 | in order | 8192 |
| batched/qwen2.5-7b-4bit-h/nvidia_h100/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H100 80GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_h100/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H100 80GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_h100/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H100 80GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_h200/s64_b128.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H200 141GB | 128 | in order | 8192 |
| batched/qwen2.5-7b-4bit-h/nvidia_h200/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H200 141GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_h200/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H200 141GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_h200/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA H200 141GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_l4/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA L4 24GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_l4/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA L4 24GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_l4/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA L4 24GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_4090/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 4090 24GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_4090/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 4090 24GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_4090/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 4090 24GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_5090/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 5090 32GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_5090/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 5090 32GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_5090/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA GeForce RTX 5090 32GB | 8 | in order | 512 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000/s64_b128.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA RTX PRO 6000 Blackwell 96GB | 128 | in order | 8192 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000/s64_b32.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA RTX PRO 6000 Blackwell 96GB | 32 | in order | 2048 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000/s64_b64.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA RTX PRO 6000 Blackwell 96GB | 64 | in order | 4096 |
| batched/qwen2.5-7b-4bit-h/nvidia_rtx_pro_6000/s64_b8.log.gz | batch | Qwen2.5-7B 4-bit (h) | W64xB | NVIDIA RTX PRO 6000 Blackwell 96GB | 8 | in order | 512 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b1.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 1 | in order | 128 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b16.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 16 | in order | 2048 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 32 | in order | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 32 | shuffled slots | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b32_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 32 | staggered joins | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 64 | in order | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 64 | shuffled slots | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b64_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 64 | staggered joins | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w128_b8.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10 | 8 | in order | 1024 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b1.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 1 | in order | 512 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 16 | in order | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 16 | shuffled slots | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b16_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 16 | staggered joins | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 32 | in order | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 32 | shuffled slots | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b32_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 32 | staggered joins | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 64 | in order | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 64 | shuffled slots | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b64_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 64 | staggered joins | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10/w512_b8.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10 | 8 | in order | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b1.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 1 | in order | 128 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b16.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 16 | in order | 2048 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 32 | in order | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 32 | shuffled slots | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b32_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 32 | staggered joins | 4096 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 64 | in order | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 64 | shuffled slots | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b64_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 64 | staggered joins | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w128_b8.log.gz | batch | Qwen2.5-7B 4-bit (g) | W128 | NVIDIA A10G | 8 | in order | 1024 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b1.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 1 | in order | 512 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 16 | in order | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 16 | shuffled slots | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b16_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 16 | staggered joins | 8192 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 32 | in order | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 32 | shuffled slots | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b32_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 32 | staggered joins | 16384 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 64 | in order | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64_shuffled.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 64 | shuffled slots | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b64_staggered.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 64 | staggered joins | 32768 |
| batched/qwen2.5-7b-int4-g/nvidia_a10g/w512_b8.log.gz | batch | Qwen2.5-7B 4-bit (g) | W512 | NVIDIA A10G | 8 | in order | 4096 |

122 logs, 874688 rows.
