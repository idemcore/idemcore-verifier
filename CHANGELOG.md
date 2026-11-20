# Changelog

## 0.4.0 (2026-11-20)

* Format v2 only. The verifier checks `FORMAT idemcore-log/v2` logs
  (SHA-256 per position and `CHAIN`). Logs in the earlier format are
  reported as "not a format v2 log" and are no longer checked; use the
  re-issued format v2 log of the same run.
* `seal` command removed.
* `samples/` now holds format v2 logs: 11 x86-64 CPU logs (Qwen2.5-0.5B
  8-bit W3260 and W240, Qwen2.5-7B 8-bit W512 and first 64, Qwen2.5-7B
  4-bit (g) W512 and first 128, Qwen2.5-7B 4-bit (h) W64), each with an
  independent second run where available, and 7 pairs.
* `samples/` adds the re-issued format v2 GPU and phone logs: 106 NVIDIA GPU
  logs (37 single-stream, 69 batched, gzip-compressed) and 5 Galaxy Z Fold5
  CPU logs. Self-check: 122 logs, 874,688 rows, 109 pairs. Qwen2.5-7B 4-bit
  (g4) is withdrawn (model file no longer available). Still pending: see
  EVIDENCE.md.
* SPEC.md, README.md, EVIDENCE.md and RESULTS.md describe format v2 only.

## 0.3.7 (2026-11-20)

* New log format v2 (`idemcore-log/v2`), recommended for new logs: SHA-256
  for every per-position digest and a SHA-256 `CHAIN` line over the format
  tag and every position line (positions, order and digests). Canonical line
  form, so `CHAIN` can be recomputed with `sha256sum`. Batched v2 logs use
  `CHAIN <s>` lines and a SHA-256 `STREAMS` digest.
* Optional SHA-256 `SEAL` line for existing v1 logs and a `seal` command that
  adds one without changing `ALL`.
* Reference writer `format_v2_log()` and `step_digest()` in
  `idemcore_verify.core`; example vector `tests/vectors/v2_example.log`.
* Format v1 is now described as the legacy 64-bit checksum format. Its
  behaviour is unchanged: all 127 published logs and 83 pairs pass.
* CLI output names the format and counts positions
  (`format v1, 512 positions, ALL ...`); comparing logs of different formats
  is refused with a clear message.
* Documentation wording cleanup.

## 0.3.6 (2026-11-11)

* New public logs: Qwen2.5-7B 4-bit (h), 256 generations (temperature 0.7, top-k 50, top-p 0.90, 128 new positions) on NVIDIA A10, L40S, A100, H100, H200, RTX PRO 6000, L4 and B200. Every log has `ALL 8774afd4535d0cb7`. All 7 pairs against the A10 log are identical (37,800 rows each, including the checked prompt positions).
* The well-formedness check on an optional legacy field no longer applies a fixed upper limit. Log format unchanged; existing logs and hashes are unaffected.

## 0.3.5 (2026-11-11)

* Documentation cleanup.

## 0.3.4 and earlier

See the GitHub releases.
