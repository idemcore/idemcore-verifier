# TODO

* **NVIDIA H100, batched.** Run Qwen2.5-7B 4-bit (g) batched at B = 1, 8, 16,
  32, 64 with shuffled and staggered schedules; add the logs under
  `samples/batched/qwen2.5-7b-int4-g/nvidia_h100/` (format v2), rows to
  `HASHES.tsv` and `PAIRS.tsv`, and the result to EVIDENCE.md.
* **More models.** Qwen2.5-1.5B (or 0.5B) and a ~14B model with the same
  cross-device and batched evidence.
* **Re-issue the remaining evidence in format v2.** gpt-oss-20b and
  gpt-oss-120b x86-64 CPU references, Galaxy Z Fold5 7B 8-bit first 64,
  Snapdragon X Plus logs (Windows line endings), and a
  second device for Idemcore 35B (see EVIDENCE.md).
