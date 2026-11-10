# Results (2026-10-30)

All numbers below were measured by us and re-read from raw run logs. Method
details: [METHODOLOGY.md](METHODOLOGY.md). Anything we could not re-verify is
marked **unverified** and is not used as a headline number. Project site:
<https://idemcore.net>.

Every bit-exactness claim here is backed by raw logs in `samples/`. The full
hash tables per device, workload and batch size are in
[EVIDENCE.md](EVIDENCE.md), and `make verify` (or
`python3 -m idemcore_verify samples`) recomputes all of them from the logs
and prints PASS or FAIL.

Section 2 is single-stream decode (batch 1); batched serving is in section 2b.
Cloud GPU clocks varied by up to ±30%
between sessions (see "Variance"), so treat cross-session differences under
~10% as noise.

## 1. Bit-exactness

Every published pair in [samples/](samples/) passes `./verify_samples.sh`:
both per-token hashes (`h` and `hc`) are identical at every compared
position.

| Model | Devices with identical hashes | Positions compared |
|---|---|---|
| Qwen2.5-0.5B-Instruct, 8-bit | x86-64 CPU, NVIDIA T4, Windows 11 ARM64 (Snapdragon X Plus), Android (Galaxy Z Fold5, Snapdragon 8 Gen 2) | 3260 (T4, Fold5; logs published); 240 (Windows ARM64, log published; its 3260-position run is a written record only, no raw log) |
| Qwen2.5-7B-Instruct, 8-bit | x86-64 CPU, NVIDIA A10, Galaxy Z Fold5 | 512 (A10), 64 (Fold5) |
| Qwen2.5-7B-Instruct, 4-bit (g) | x86-64 CPU, NVIDIA A10, Galaxy Z Fold5 | 512 (A10), 128 (Fold5) |
| Qwen2.5-7B-Instruct, 4-bit (g4) | x86-64 CPU, NVIDIA A10G | 512 |
| gpt-oss-20b (MoE) | x86-64 CPU, NVIDIA L40S | 512 |
| gpt-oss-120b (MoE) | x86-64 CPU (128-token spot check), NVIDIA H100 | 128 |
| Qwen2.5-7B-Instruct, 4-bit (h) | NVIDIA H100, H200, A100, B200, L4, RTX PRO 6000, GeForce RTX 3090, RTX 4090, RTX 5090 | 64 per GPU; batched B = 8–128 (stream `ALL` digests equal across GPUs) |
| Qwen2.5-7B-Instruct, 4-bit (h), 256 generations (temperature 0.7, top-k 50, top-p 0.90, 128 new tokens) | NVIDIA A10, L40S, A100, H100, H200, RTX PRO 6000, L4, B200 | 37,800 positions per GPU; every log has `ALL 8774afd4535d0cb7` |
| Idemcore 27B | NVIDIA A100, H200, GeForce RTX 3090, RTX 5090 (logs published); `ALL` equal to the H100 reference digest | 5120 per GPU (3 test sets) |
| Idemcore 35B (MoE) | NVIDIA A100 (log published); `ALL` equal to the H100 reference digest | 5120 (3 test sets) |

Qwen2.5-7B 4-bit (g) on the Fold5 matches the x86 log on the first 128
positions (phone log `ALL 8d694e5c633851cc`).

The 256-generation logs (temperature 0.7, top-k 50, top-p 0.90, 128 new
tokens) are in `samples/qwen2.5-7b-4bit-h-seeded/`. All eight GPUs give
`ALL 8774afd4535d0cb7`, and each of the seven pairs against the A10 log
is identical at 37,800/37,800 positions. The same 256 generations were
also submitted in reverse order, and eight of them were also run one at
a time; those repeats matched pass A on every GPU. NVIDIA T4 was not
run: this model is not supported on T4 in the engine used (a coverage
gap, not a failure). GeForce RTX 3090, 4090 and 5090 were not offered
by the machine pool used, so they were not run. The L4 log is from
2026-11-11; the other seven are from 2026-11-10.



### Control: other engines

* llama.cpp b11972, Qwen2.5-1.5B Q8_0, same x86 machine, two builds for
  different x86 CPU generations: 0 of 1127 positions bit-identical, max |Δ logprob| 0.82 nat,
  28 argmax flips. No server flag we tried (`-fa off`, `--no-repack`, f32 KV)
  made the two builds agree. x86 vs Snapdragon X (ARM64): 0/1127 identical
  top-50 lists, 24 argmax flips. Re-runs on the same machine were identical.
* HF transformers (gpt-oss): token-by-token decode vs one parallel forward
  pass on the same GPU disagree on argmax at 27/512 (20b) and 29/512 (120b)
  positions.

## 2. Speed (single stream, tokens/s, higher is better)

### Qwen2.5-7B-Instruct on NVIDIA A10 (24 GB)

Idemcore: 512 teacher-forced decode steps. llama.cpp server and vLLM: 3 × 256
greedy tokens with EOS ignored, pooled inter-token latency (after one warm-up).
Idemcore rows ran in a different session from the baselines (Idemcore 4-bit
mean SM clock 1652 MHz; baselines' max SM clock 1695 MHz).

| Engine | tok/s | p50 ms | p99 ms |
|---|---|---|---|
| **Idemcore 4-bit (g), hashing on** | **92.98** | 10.77 | 10.87 |
| llama.cpp Q4_K_M (b11977) | 90.30 | 11.09 | 11.83 |
| vLLM 0.11.0 AWQ | 87.99 | 11.30 | 12.16 |
| llama.cpp Q8_0 | 58.52 | 17.11 | 17.90 |
| **Idemcore 8-bit, hashing on** | **56.95** | 17.56 | 18.07 |
| vLLM 0.11.0 fp16 | 30.44 | 32.80 | 33.60 |

The vLLM rows were measured with vLLM 0.11.0 on 2026-10-30 and have not been re-measured on current vLLM releases; treat them as a dated reference point, not a current comparison.

### Qwen2.5-7B-Instruct on NVIDIA A10G (24 GB), both at 1710 MHz SM

| Engine | tok/s | p50 ms | p99 ms | J/token (board) | J/token (above idle) |
|---|---|---|---|---|---|
| **Idemcore 4-bit (g4), hashing on** | **98.64** | 10.15 | 10.27 | 1.61 | 1.45 |
| llama-cpp-python 0.3.4 Q4_K_M | 92.37 | 10.75 | 13.12 | 2.53 | 2.40 |

Caveat: the llama.cpp A10G run has only 129 latency samples and 11 power
samples, and power is sampled coarsely (nvidia-smi). Treat J/token as
indicative only.

### gpt-oss (MoE, teacher-forced 512 positions)

| Model / GPU | Idemcore tok/s | p50 ms | p99 ms | HF transformers (MXFP4) median ms/token |
|---|---|---|---|---|
| gpt-oss-20b / L40S | 72.1–72.2 | 13.9 | 14.0 | ~50 |
| gpt-oss-120b / H100 | 37.1–37.3 | 26.9 | 27.4 | 77–80 |

HF transformers is a correctness reference, not an optimized server; we did
not benchmark vLLM/SGLang on gpt-oss.

### Edge devices, Qwen2.5-0.5B 8-bit

| Device | 1 thread | best multi-thread |
|---|---|---|
| x86-64 cloud CPU | 14.29 tok/s | 46.6 (8 threads) |
| Windows 11 ARM64, Snapdragon X Plus X1P64100 | 21.40 | 54.82 (4 threads) |
| Galaxy Z Fold5 (SM8550, Android 16, Termux) | 11.00 | 3.62 (8 threads; a known multi-thread regression on this phone, under investigation) |

GPU: T4 84.78 tok/s; A10 180.38 tok/s (the A10 run used a different
workload and has no CPU pair in this release).

Qwen2.5-7B 8-bit on the Fold5: 64/64 positions bit-identical to x86,
0.25 tok/s (p50 2.96 s, p99 11.0 s), peak RSS 3.76 GB, peak 85.6 °C. This is
a correctness demonstration, not a usable speed.

Qwen2.5-7B 4-bit (g) on the Fold5 (Samsung SM-F946B, 4 big cores):
128/128 positions bit-identical to x86, 3.39 tok/s including the
first token (3.73 tok/s steady state; first token 3.6 s), p50 260 ms,
p99 435 ms, peak RSS about 4.5 GB, peak thermal zone 90.7 °C. That is about
13.6× the 8-bit run on the same phone. In a later session, two repeat runs on the
Fold5 each matched x86 on all 128 positions with the same `ALL` digest; that session had less free memory and
was slower, so 3.39 tok/s remains the reference phone speed.

Phone energy, **estimate**: read from the battery fuel gauge
(`termux-battery-status`, 2 s sampling), not a power meter. Idle 2.62 W
(n=19), during decoding 8.43 W (n=16): about 2.49 J/token total and
1.71 J/token above idle. On this phone the gauge reports current in µA at idle
and in mA under load; we normalize before multiplying by voltage.

**H100 serving figures.** The H100 7B serving figures on idemcore.net (3166–4775 tok/s) come from a newer engine build measured on the evening of 2026-11-01. Paper v1.1 reports 2729–4008 tok/s from an earlier build measured the same day. Both are real measurements of different builds.

## 2b. Batched serving (Qwen2.5-7B 4-bit (g), NVIDIA A10G)

Batched GPU serving, A10G at 1710 MHz SM. `B` independent streams,
512 teacher-forced positions each, both hashes computed for every token of
every stream. Latency is the GPU step time for the whole batch.

| B | Idemcore aggregate tok/s | Idemcore per-stream tok/s | step p50 / p99 ms | vLLM 0.11.0 AWQ aggregate tok/s |
|---|---|---|---|---|
| 1 | 92.69 | 92.69 | 10.81 / 10.88 | 87.0–87.8 |
| 8 | 641.37 | 80.17 | 12.49 / 12.61 | 645–651 |
| 16 | 1057.55 | 66.10 | 15.16 / 15.28 | 1187–1189 |
| 32 | 1371.69 | 42.87 | 23.42 / 23.57 | 1993–2012 |
| 64 | 1413.34 | 22.08 | 45.48 / 45.70 | not run |

* At B=1 Idemcore is about 6% faster than vLLM AWQ; at B=8 they are on par.
  **vLLM is faster from B=16 on**: 1.12× at 16 and about 1.46× at 32
  (per stream 41 vs 62 tok/s at B=32).
* llama.cpp server Q4_K_M with 8 slots (`-np 8 -cb`): 298.1 tok/s aggregate at
  B=8. That run landed on an NVIDIA A10 (1695 MHz) from the same cloud pool,
  not an A10G.
* Step-time p99 is within 1% of p50 at every batch size (within about 4% when
  streams join at staggered times).
* **Caveats.** Idemcore timings are teacher-forced GPU step times; vLLM's are
  client-side generation timings (wall time including prefill), ranges over
  repeated runs. The comparison is indicative. One vLLM version (0.11.0) was
  used, at default settings; one GPU type; 8 prompts
  × 512 greedy tokens.

**Bit identity under batching.** At B = 1, 8, 16, 32 and 64, every per-token
`h` and `hc` of every stream matched the single-stream x86-64 log
(0 mismatches), also with shuffled slot order and with streams joining at
staggered times into reused slots. On the 128-position workload used for the
phone, the chained digest is `ALL 8d694e5c633851cc` at every batch size, the
same as x86 and the Fold5.

**Control: other serving stacks under batching.** 8 prompts × 512 greedy
tokens (EOS ignored), each compared with its own first solo run:

| Engine (default settings unless noted) | Schedules | Outcome in our runs |
|---|---|---|
| vLLM 0.11.0 AWQ (prefix caching on) | solo repeat, B=8 ×3, shuffled order, mixed batches of 12 and 32, staggered arrivals | not bit-reproducible: greedy output changed for some prompts in at least one schedule; token-identical B=8 repeats still differed in logprobs |
| vLLM 0.11.0 AWQ, prefix caching off | same | not bit-reproducible: outputs changed in at least one schedule; serial solo repeats also differed |
| llama.cpp server Q4_K_M, `-np 8 -cb` | solo repeat, B=8 ×3, shuffled, staggered | solo repeat bit-identical; batched runs were not bit-identical to solo runs |
| Idemcore 4-bit (g) | B=1–64, shuffled slots, staggered joins with slot reuse | bit-identical: 0 mismatches against the single-stream x86 log |

These observations describe these specific runs; they are **not** general
divergence rates. The supported claim is narrow: at default settings these stacks were not
bit-reproducible across batch composition or schedule in our runs.
We did not test optional settings of these engines. The batched raw logs (A10G and A10, 40 files) are in `samples/batched/`; per-run digests are in [EVIDENCE.md](EVIDENCE.md).

## 3. Quality

Perplexity on the same 512-position WikiText-2 slice (lower is better):

| Model | Idemcore | Other engine, same slice |
|---|---|---|
| Qwen2.5-7B 8-bit | 16.84 | — |
| Qwen2.5-7B 4-bit (g) | 16.96 | llama.cpp Q4_K_M 17.52 |
| Qwen2.5-7B 4-bit (g4) | 17.21 | llama.cpp Q4_K_M 17.52 |
| gpt-oss-20b | 78.41 | HF transformers MXFP4 77.35 |
| gpt-oss-120b | 146.75 | HF transformers MXFP4 138.15 |

Absolute gpt-oss PPL on this raw-text slice is high for both engines; only the
relative gap is meaningful. The gpt-oss-120b gap is the main quality item we
are working on. The slice has only 512 positions; differences under about 1%
are not significant.

## 4. Variance

In one A10 session the SM clock ranged 387–1307 MHz; wall-clock throughput of
the same binary ranged 57.9–89.4 tok/s while per-step GPU latency stayed
≈10.6 ms. We report the session with stable clocks and disclose this range.
