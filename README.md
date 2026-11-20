# idemcore-verifier

[![verify](https://github.com/idemcore/idemcore-verifier/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/idemcore/idemcore-verifier/actions/workflows/verify.yml)

**Check, without trusting us, that two machines produced bit-identical LLM inference.**

Project site: <https://idemcore.net>

Idemcore is an inference engine where the same model, prompt, and
settings give the *same bits* on an x86 laptop, an ARM phone, and NVIDIA GPUs
from Turing to Blackwell. At every position it scores or generates, it emits
two digests of its output at that position. A run log is a list of these
digests plus one chained digest, all SHA-256 (format v2, `CHAIN` line).

This repository is the **open half** of Idemcore:

* the log format and hash protocol ([SPEC.md](SPEC.md)),
* a small, dependency-free Python verifier (`idemcore_verify/`),
* the measurement methodology ([METHODOLOGY.md](METHODOLOGY.md)),
* raw per-position logs in format v2 (`samples/`) and the results table
  ([RESULTS.md](RESULTS.md)).

The inference engine itself is not in this repository and is not open source.
You do not need it to check a claim: the verifier only needs two logs.

## Reproduce it yourself

You need `git` and Python ≥ 3.9. No GPU, no model and no third-party package.

```sh
# 1. get the verifier and the sample logs
git clone https://github.com/idemcore/idemcore-verifier.git
cd idemcore-verifier

# 2. optional: a clean virtual environment and the `idemcore-verify` command
python3 -m venv .venv && . .venv/bin/activate
pip install .

# 3. recompute every published CHAIN and re-check every published pair
python3 -m idemcore_verify samples        # same as: make verify  or  sh verify_samples.sh

# 4. check one pair yourself: two independent runs of Qwen2.5-7B 4-bit
python3 -m idemcore_verify compare samples/qwen2.5-7b-int4-g/x86_64.log \
                                   samples/qwen2.5-7b-int4-g/x86_64_run2.log

# 5. the unit tests, including a tamper test
python3 -m unittest discover -s tests
```

Expected output of step 3:

```
checked 128 logs (879132 rows) and 115 pairs
PASS: every published CHAIN recomputes and every pair is bit-identical
```

and of step 4:

```
OK   samples/qwen2.5-7b-int4-g/x86_64.log: format v2, 512 positions, CHAIN cf10ae9c81731610ad975c49852cbaa82ad61fdf94fd9cf3b1180700bef8c22d (recomputed cf10ae9c81731610ad975c49852cbaa82ad61fdf94fd9cf3b1180700bef8c22d)
OK   samples/qwen2.5-7b-int4-g/x86_64_run2.log: format v2, 512 positions, CHAIN cf10ae9c81731610ad975c49852cbaa82ad61fdf94fd9cf3b1180700bef8c22d (recomputed cf10ae9c81731610ad975c49852cbaa82ad61fdf94fd9cf3b1180700bef8c22d)
MATCH: 512/512 positions identical (mode exact; only-in-ref 0, only-in-cand 0)
```

Step 3 recomputes every published `CHAIN` in
[samples/HASHES.tsv](samples/HASHES.tsv) from the shipped logs and re-checks
every pair in [samples/PAIRS.tsv](samples/PAIRS.tsv). To prove the check is not a rubber
stamp, edit any hex digit in a log and run it again: the chain breaks.

`idemcore-verify samples` looks for `./samples` in the current directory; run
it from the repository root, or pass `--dir path/to/samples`. `make` is not
required; every `make` target is a one-line Python command.

### Check a live answer from api.idemcore.net

The hosted API (`https://api.idemcore.net/v1`, OpenAI-compatible) attaches a
receipt to every answer, and `GET /v1/receipts/{id}/log` returns that answer's
per-position log; `?log_format=v2` returns its format v2 form, which this
verifier checks. Access
needs an API key: sign in to the console at
<https://console.idemcore.net/#/login> and create one. With a key, save the
log and run:

```sh
curl -s "https://api.idemcore.net/v1/receipts/RECEIPT_ID/log?log_format=v2" \
  -H "Authorization: Bearer $IDEMCORE_API_KEY" | jq -r .log_text > answer.log
python3 -m idemcore_verify check answer.log
python3 -m idemcore_verify compare answer.log your_rerun.log
```

### Install as a package

The verifier is published on PyPI as
[`idemcore-verify`](https://pypi.org/project/idemcore-verify/) (console script of
the same name):

```sh
pip install idemcore-verify
idemcore-verify --version
idemcore-verify check run.log
idemcore-verify compare reference.log candidate.log
```

The package contains only the verifier; the sample logs ship with this
repository.

Every published `CHAIN` and the re-issue status of earlier runs: [EVIDENCE.md](EVIDENCE.md).

Requires Python ≥ 3.9, standard library only.

## What the verifier checks

1. **Well-formedness** – the log is format v2: a `FORMAT idemcore-log/v2`
   line, position lines with four fields in canonical form, both digests
   SHA-256 (64 hex), no duplicate positions, exactly one `CHAIN` line.
2. **Chain integrity** – it recomputes `CHAIN` from the position lines;
   editing a single line breaks it. `CHAIN` can also be recomputed with
   `sha256sum` alone (see [SPEC.md](SPEC.md)).
3. **Agreement** – it compares a candidate log against a reference log
   position by position, keyed by `(payload, position)`, and prints the first
   divergence (which position, which field). `--subset` allows a short spot check
   (e.g. 128 CPU positions against a 512-position GPU run).

A match on `h` means the two machines produced the **same output for the whole
vocabulary** at that position, not just the same top choice. A match on `hc`
means the second per-position hash, which covers the engine's choice
output, is also identical.

## Log format

`FORMAT idemcore-log/v2`: every per-position digest is SHA-256 (64 hex) and
the log ends with one `CHAIN` line, the SHA-256 over the format tag and every
position line. The chain covers positions, order and digests, and can be
recomputed without this tool:

```sh
(printf 'idemcore-log/v2\n'; grep -E '^[0-9]' run.log) | sha256sum
```

Example: [tests/vectors/v2_example.log](tests/vectors/v2_example.log)
(synthetic test vector). Full text: [SPEC.md](SPEC.md).

Logs in the earlier format (no `FORMAT` line, `ALL` chain line) are no
longer checked by this verifier; it reports them as not format v2. The
published runs have been re-issued as format v2 logs of the same runs; the
few that are not yet re-issued are listed in [EVIDENCE.md](EVIDENCE.md).

## Published results

The last column says whether the format v2 log of that result is in
`samples/` today ([EVIDENCE.md](EVIDENCE.md) has every `CHAIN`).

| Model | Reference | Candidate | Positions | Result | Format v2 log |
|---|---|---|---|---|---|
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | NVIDIA T4 | 3260 | identical | in `samples/` |
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | Galaxy Z Fold5 (Android) | 3260 (full run) and 240 | identical | in `samples/` |
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | Windows 11 ARM64 laptop (Snapdragon X Plus): CPU, and Adreno X1-85 GPU | 240 (CPU and GPU), 3260 (GPU) | identical | in `samples/` |
| Qwen2.5-7B, 8-bit | x86-64 CPU | NVIDIA A10 | 512 | identical | in `samples/` |
| Qwen2.5-7B, 8-bit | x86-64 CPU | Galaxy Z Fold5 (Android) | 64 (prefix) | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | Windows 11 ARM64 laptop (Snapdragon X Plus), Adreno X1-85 GPU | 128 (prefix) | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | NVIDIA A10 | 512 | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | Galaxy Z Fold5 (Android), 3 runs | 128 (prefix) | identical | in `samples/` |
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | x86-64 CPU, independent second run | 3260 and 240 | identical | in `samples/` |
| Qwen2.5-7B, 8-bit | x86-64 CPU | x86-64 CPU, independent second run (6 threads) | 512 | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | x86-64 CPU, independent second run (6 threads) | 512 | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | NVIDIA A10G and A10, batched B = 1–64, shuffled and staggered (40 logs) | every row of every stream | identical | in `samples/` |
| gpt-oss-20b (MoE) | x86-64 CPU | NVIDIA L40S | 512 | identical | in `samples/` |
| gpt-oss-120b (MoE) | x86-64 CPU (spot check) | NVIDIA H100 | 128 of 512 | identical | GPU log in `samples/`; CPU spot check pending |
| Qwen2.5-7B, 4-bit (h) | x86-64 CPU and NVIDIA H100 | NVIDIA H200, A100, B200, L4, RTX PRO 6000, GeForce RTX 3090, RTX 4090, RTX 5090 | 64 per GPU; batched B = 8–128 (29 logs), every row of every stream against the x86-64 CPU log | identical | in `samples/` |
| Qwen2.5-7B, 4-bit (h), 256 generations (temperature 0.7, top-k 50, top-p 0.90, 128 new positions) | NVIDIA A10 | NVIDIA L40S, A100, H100, H200, RTX PRO 6000, L4, B200 | 37,800 rows per GPU (prompt positions and 128 new positions); every log has the same `CHAIN` | identical | in `samples/` |
| Idemcore 27B | NVIDIA A100 | NVIDIA H200, GeForce RTX 3090, RTX 5090 | 3 test sets, 5120 positions per GPU | identical | in `samples/` |
| Idemcore 35B (MoE) | – | NVIDIA A100 | 3 test sets, 5120 positions | `CHAIN` published; no second device in format v2 yet | in `samples/` |

Details per file: [samples/MANIFEST.md](samples/MANIFEST.md).

**Batched GPU serving.** With batched GPU serving, Qwen2.5-7B 4-bit
on an NVIDIA A10G serves up to 64 concurrent streams, and every stream's
per-position hashes match a single-stream x86-64 run at batch sizes 1, 8, 16, 32
and 64, including shuffled slot order and staggered joins (0 mismatches).
The same holds on an NVIDIA A10. Details and caveats:
[RESULTS.md](RESULTS.md#2-phone-runs-and-batched-serving).
The batched logs are in `samples/batched/` in format v2.

## Methodology

* How the results were measured (workloads, baselines, quality):
  [METHODOLOGY.md](METHODOLOGY.md).
* Results and their caveats: [RESULTS.md](RESULTS.md); every hash, per device,
  workload and batch size: [EVIDENCE.md](EVIDENCE.md).

## Paper

Don Wick, *Idemcore: Bit-Identical LLM Inference across Phones, Laptops and
Datacenter GPUs, with Open Verification Logs*, preprint version 1.3, Zenodo,
2026. DOI: [10.5281/zenodo.24392595](https://doi.org/10.5281/zenodo.24392595)
(all versions: [10.5281/zenodo.23851128](https://doi.org/10.5281/zenodo.23851128)).
Citation metadata: [CITATION.cff](CITATION.cff).

## What this does **not** prove

* The logs are produced by our engine. A matching pair shows two runs agree;
  it does not prove *which* program produced them. To check a provider, re-run
  the same request on hardware you control (or ask a second party to) and
  compare logs.
* A digest log shows that two runs agree; on its own it does not prove which
  device produced a log or when.

## License

Apache-2.0 for everything in this repository (verifier, spec, methodology,
sample logs). See [LICENSE](LICENSE). Idemcore's inference engine and model
files are proprietary and are not covered by this license.

Contact: Don Wick — don.wick@idemcore.net · Website: <https://idemcore.net>
· Security reports: [SECURITY.md](SECURITY.md) · Mismatch reports: open an
issue with the "Hash mismatch" template.

Copyright 2026 Don Wick.
