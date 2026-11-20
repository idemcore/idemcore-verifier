# TODO

* **NVIDIA H100, batched.** Run Qwen2.5-7B 4-bit (g) batched at B = 1, 8, 16,
  32, 64 with shuffled and staggered schedules; add the logs under
  `samples/batched/qwen2.5-7b-int4-g/nvidia_h100/`, rows to `HASHES.tsv` and
  `PAIRS.tsv`, and the throughput to EVIDENCE.md.
* **More models.** Qwen2.5-1.5B (or 0.5B) and a ~14B model with the same
  cross-device and batched evidence.
* **Format v2 emission from the engine.** Verifier 0.3.7 defines and checks
  format v2 (SHA-256). Next: the engine and the hosted API emit v2 logs, and
  new evidence runs are published in v2 alongside the existing v1 logs.
