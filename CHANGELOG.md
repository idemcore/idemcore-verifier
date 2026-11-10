# Changelog

## 0.3.6 (2026-11-11)

* New public logs: Qwen2.5-7B 4-bit (h), 256 generations (temperature 0.7, top-k 50, top-p 0.90, 128 new tokens) on NVIDIA A10, L40S, A100, H100, H200, RTX PRO 6000, L4 and B200. Every log has `ALL 8774afd4535d0cb7`. All 7 pairs against the A10 log are identical (37,800 positions each).
* The well-formedness check on an optional legacy field no longer applies a fixed upper limit. Log format unchanged; existing logs and hashes are unaffected.

## 0.3.5 (2026-11-11)

* Documentation cleanup.

## 0.3.4 and earlier

See the GitHub releases.
