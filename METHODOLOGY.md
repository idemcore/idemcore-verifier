# Measurement methodology

Everything here can be reproduced with public tools. The numbers in
[RESULTS.md](RESULTS.md) were collected this way.

## Workloads

* **Qwen2.5-0.5B-Instruct**, 20 English text payloads, 3260 tokens, 11 899
  UTF-8 bytes in total (10 short documents and 10 retrieval contexts).
  "sub240" runs score the first 12 tokens of every payload (240 positions).
* **Qwen2.5-7B-Instruct** and **gpt-oss-20b / gpt-oss-120b**: a WikiText-2
  slice cut into 4 payloads of 128 tokens (512 scored positions).
* Every position is scored with teacher forcing (the true next token is fed
  back), so all engines see identical inputs and the logs line up by
  `(payload, position)`.

## Bit-exactness

* The reference is the x86-64 CPU build (1 to 16 threads). The
  candidate is the same model file run on another device or another thread
  count.
* A pair counts as **identical** only if `h` and `hc` (and `freq` and
  `total`, when both logs carry them) agree at every compared position
  (`idemcore_verify compare`). The published sample logs are hash-only.
* For the largest models, CPU reference time is limited, so we compare a
  spot-check subset (gpt-oss-120b: first 32 positions of each of the 4
  payloads, 128 positions). These runs are labelled "subset".

## Speed

* Single stream, batch size 1, decode one token per step, 512 steps per run.
* Per-token latency is measured around each step, from submitting the step to
  having the logits and both hashes back on the host.
  We report mean throughput (tok/s = 1 / mean latency), p50 and p99.
* Every reported run, and every log in this repo, was produced with full
  per-token hashing (`h` and `hc` for every token).
* Baselines on the same GPU type, same model, same 512-token workload:
  * llama.cpp `llama-server`, build b11977 (commit 7ac5727d6), all layers on
    GPU, default flags; inter-token latency from the streamed response.
  * vLLM 0.11.0, single request, streamed; inter-token latency.
  * Hugging Face transformers (gpt-oss only), MXFP4, greedy decode with KV cache.
* Cloud GPUs (NVIDIA T4, A10, A10G, L40S, H100) are rented on demand. Two GPUs
  of the same name can run at different clocks; we record the SM clock and
  report the GPU model for every number. Run-to-run spread on the same GPU type
  was up to ±30% in some sessions; we publish the full spread where we saw it.

## Energy

* `nvidia-smi --query-gpu=power.draw,clocks.sm,temperature.gpu` sampled about
  every 100 ms during the run, and for several seconds of idle before it.
* We report **board energy per token** = mean power during the run / tok/s,
  and **above-idle energy per token** = (mean run power − mean idle power) /
  tok/s. Power sampling at this rate is coarse; treat differences below ~10%
  as noise.
* On Android we record thermal zones and `MemAvailable`. Phone J/token is an
  **estimate** from the battery fuel gauge (`termux-battery-status`, about
  every 2 s, idle then run): mean |current| × voltage per phase, divided by
  tok/s. Some Samsung gauges report µA at idle and mA under load; any reading
  below 100000 in magnitude is treated as mA. This is not a power meter.

## Quality

* Perplexity (PPL) and top-1 agreement on the same 512 positions, computed
  from each engine's log-probability of the true token and its argmax.
* Top-1 agreement is the fraction of positions where our argmax equals the
  reference engine's argmax (Hugging Face bf16 / MXFP4).
