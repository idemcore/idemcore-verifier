# Results (2026-10-30)

All numbers below were measured by us and re-read from raw run logs. Method
details: [METHODOLOGY.md](METHODOLOGY.md). Anything we could not re-verify is
marked **unverified** and is not used as a headline number. Project site:
<https://idemcore.net>.

Verifier 0.4.0 checks format v2 logs only. The logs behind section 1 have
been re-issued in format v2; [EVIDENCE.md](EVIDENCE.md) lists them and the few
that are still pending, and `make verify` (or `python3 -m idemcore_verify samples`)
recomputes all of them and prints PASS or FAIL. Results whose logs are not yet
re-issued are results as measured, pending a format v2 log.

Section 2 covers bit identity under concurrent (batched) serving; section 3 is
quality. This file reports correctness and quality results only.

## 1. Bit-exactness

Each row below was measured with both per-position hashes (`h` and `hc`)
identical at every compared position. Format v2 logs available now: see
[EVIDENCE.md](EVIDENCE.md).

| Model | Devices with identical hashes | Positions compared |
|---|---|---|
| Qwen2.5-0.5B-Instruct, 8-bit | x86-64 CPU, NVIDIA T4, Windows 11 ARM64 (Snapdragon X Plus), Android (Galaxy Z Fold5, Snapdragon 8 Gen 2) | 3260 (T4, Fold5; format v2 logs published); 240 (Windows ARM64; format v2 log pending; its 3260-position run is a written record only, no raw log) |
| Qwen2.5-7B-Instruct, 8-bit | x86-64 CPU, NVIDIA A10, Galaxy Z Fold5 | 512 (A10), 64 (Fold5; format v2 log pending) |
| Qwen2.5-7B-Instruct, 4-bit (g) | x86-64 CPU, NVIDIA A10, Galaxy Z Fold5 | 512 (A10), 128 (Fold5) |
| gpt-oss-20b (MoE) | x86-64 CPU, NVIDIA L40S | 512 |
| gpt-oss-120b (MoE) | x86-64 CPU (128-position spot check), NVIDIA H100 | 128 |
| Qwen2.5-7B-Instruct, 4-bit (h) | NVIDIA H100, H200, A100, B200, L4, RTX PRO 6000, GeForce RTX 3090, RTX 4090, RTX 5090 | 64 per GPU; batched B = 8–128 (stream chain digests equal across GPUs) |
| Qwen2.5-7B-Instruct, 4-bit (h), 256 generations (temperature 0.7, top-k 50, top-p 0.90, 128 new positions) | NVIDIA A10, L40S, A100, H100, H200, RTX PRO 6000, L4, B200 | 37,800 rows per GPU (prompt positions and 128 new positions); every log has the same chain digest |
| Idemcore 27B | NVIDIA A100, H200, GeForce RTX 3090, RTX 5090 (format v2 logs published) | 5120 per GPU (3 test sets) |
| Idemcore 35B (MoE) | NVIDIA A100 (format v2 logs published; no second device in format v2 yet) | 5120 (3 test sets) |

Qwen2.5-7B 4-bit (g) on the Fold5 matches the x86 log on the first 128
positions (format v2 reference for these 128 positions: `CHAIN 9320ecc5…7d01`).

The 256-generation logs (temperature 0.7, top-k 50, top-p 0.90, 128 new
positions) were run on eight GPUs; all eight give the same chain digest, and each of the seven pairs against the A10 log
is identical at 37,800/37,800 rows (prompt positions and 128 new positions). The same 256 generations were
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
* HF transformers (gpt-oss): step-by-step decode vs one parallel forward
  pass on the same GPU disagree on argmax at 27/512 (20b) and 29/512 (120b)
  positions.

## 2. Phone runs and batched serving

Qwen2.5-7B 8-bit on the Galaxy Z Fold5: 64/64 positions bit-identical to x86
(format v2 log pending), peak RSS 3.76 GB.

Qwen2.5-7B 4-bit (g) on the Fold5 (Samsung SM-F946B, 4 big cores):
128/128 positions bit-identical to x86, peak RSS about 4.5 GB. In a later
session, two repeat runs on the Fold5 each matched x86 on all 128 positions with
the same chain digest.

Batched serving of Qwen2.5-7B 4-bit (g) on an NVIDIA A10G (and A10): `B`
independent streams, 512 teacher-forced positions each, both hashes computed
for every position of every stream.

**Bit identity under batching.** At B = 1, 8, 16, 32 and 64, every per-position
`h` and `hc` of every stream matched the single-stream x86-64 log
(0 mismatches), also with shuffled slot order and with streams joining at
staggered times into reused slots. On the 128-position workload used for the
phone, the chain digest is the same at every batch size, the
same as x86 and the Fold5.

**Control: other serving stacks under batching.** 8 prompts × 512 greedy
positions (EOS ignored), each compared with its own first solo run:

| Engine (default settings unless noted) | Schedules | Outcome in our runs |
|---|---|---|
| vLLM 0.11.0 AWQ (prefix caching on) | solo repeat, B=8 ×3, shuffled order, mixed batches of 12 and 32, staggered arrivals | not bit-reproducible: greedy output changed for some prompts in at least one schedule; output-identical B=8 repeats still differed in logprobs |
| vLLM 0.11.0 AWQ, prefix caching off | same | not bit-reproducible: outputs changed in at least one schedule; serial solo repeats also differed |
| llama.cpp server Q4_K_M, `-np 8 -cb` | solo repeat, B=8 ×3, shuffled, staggered | solo repeat bit-identical; batched runs were not bit-identical to solo runs |
| Idemcore 4-bit (g) | B=1–64, shuffled slots, staggered joins with slot reuse | bit-identical: 0 mismatches against the single-stream x86 log |

These observations describe these specific runs; they are **not** general
divergence rates. The supported claim is narrow: at default settings these stacks were not
bit-reproducible across batch composition or schedule in our runs.
We did not test optional settings of these engines. The batched logs (A10G and A10, 40 files) are in `samples/batched/` in format v2.

## 3. Quality

Perplexity on the same 512-position WikiText-2 slice (lower is better):

| Model | Idemcore | Other engine, same slice |
|---|---|---|
| Qwen2.5-7B 8-bit | 16.84 | — |
| Qwen2.5-7B 4-bit (g) | 16.96 | llama.cpp Q4_K_M 17.52 |
| gpt-oss-20b | 78.41 | HF transformers MXFP4 77.35 |
| gpt-oss-120b | 146.75 | HF transformers MXFP4 138.15 |

Absolute gpt-oss PPL on this raw-text slice is high for both engines; only the
relative gap is meaningful. The gpt-oss-120b gap is the main quality item we
are working on. The slice has only 512 positions; differences under about 1%
are not significant.
