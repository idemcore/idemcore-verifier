# Measurement methodology

Everything here can be reproduced with public tools. The numbers in
[RESULTS.md](RESULTS.md) were collected this way.

## Workloads

* **Qwen2.5-0.5B-Instruct**, 20 English text payloads, 3260 positions, 11 899
  UTF-8 bytes in total (10 short documents and 10 retrieval contexts).
  "sub240" runs score the first 12 positions of every payload (240 positions).
* **Qwen2.5-7B-Instruct** and **gpt-oss-20b / gpt-oss-120b**: a WikiText-2
  slice cut into 4 payloads of 128 positions (512 scored positions).
* Every position in the workloads above is scored with teacher forcing (the
  true next input is fed back), so all engines see identical inputs and the
  logs line up by `(payload, position)`.
* **Qwen2.5-7B-Instruct, 4-bit (h), 256 generations:** 64 prompts × 4 seeds
  (1001, 1002, 1003, 1004), temperature 0.7, top-k 50, top-p 0.90, exactly
  128 new positions per generation. Each log also includes the checked prompt positions; prompts differ in length, so each generation has 144–151 rows and each file has 37,800 rows.
  Logs line up by `(generation, position)`.
  This is a generate-and-compare workload, not teacher forcing. An additional
  64-position teacher-forced request on the public 4-bit (h) workload is used
  only as an anchor to the published reference digest of that workload;
  it is not part of the pass criterion.

## Bit-exactness

* For the teacher-forced workloads, the reference is the x86-64 CPU build
  (1 to 16 threads). The candidate is the same model file run on another
  device or another thread count. For the 256-generation logs, the
  reference is the NVIDIA A10 run; each other GPU is compared with that
  log.
* A pair counts as **identical** only if `h` and `hc` agree at every
  compared position (`idemcore_verify compare`).
* For the largest models, CPU reference time is limited, so we compare a
  spot-check subset (gpt-oss-120b: first 32 positions of each of the 4
  payloads, 128 positions). These runs are labelled "subset".

## Hardware and logging

* Every log in this repo was produced with full per-position hashing (`h` and
  `hc` for every position).
* Cloud GPUs (NVIDIA T4, A10, A10G, L4, L40S, A100, H100, H200, B200, GeForce
  RTX 3090, RTX 4090, RTX 5090, RTX PRO 6000) are rented on demand. We report
  the GPU model for every log.

## Quality

* Perplexity (PPL) on the same 512 positions, computed from each engine's
  log-probability of the true next input.
