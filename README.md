# idemcore-verifier

[![verify](https://github.com/idemcore/idemcore-verifier/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/idemcore/idemcore-verifier/actions/workflows/verify.yml)

**Check, without trusting us, that two machines produced bit-identical LLM inference.**

Project site: <https://idemcore.net>

Idemcore is an integer-only inference engine: the same model, prompt, and
settings give the *same bits* on an x86 laptop, an ARM phone, and NVIDIA GPUs
from Turing to Hopper. Every token it scores or generates emits a 64-bit hash
of the full logit vector and a 64-bit hash of the integer sampling table
(CDF). A run log is a list of these hashes plus one chained digest (`ALL`).

This repository is the **open half** of Idemcore:

* the log format and hash protocol ([SPEC.md](SPEC.md)),
* a small, dependency-free Python verifier (`idemcore_verify/`),
* the measurement methodology ([METHODOLOGY.md](METHODOLOGY.md)),
* raw per-token logs from real cross-device runs (`samples/`) and the results
  table they back ([RESULTS.md](RESULTS.md)).

The inference kernel itself is not in this repository and is not open source.
You do not need it to check a claim: the verifier only needs two logs.

## Reproduce in 5 minutes

You need `git` and Python ≥ 3.9. No GPU, no model and no third-party package.

```sh
# 1. get the verifier and the sample logs (about 6 MB)
git clone https://github.com/idemcore/idemcore-verifier.git
cd idemcore-verifier

# 2. optional: a clean virtual environment and the `idemcore-verify` command
python3 -m venv .venv && . .venv/bin/activate
pip install .

# 3. recompute every published hash and re-check every published pair (~5 s)
python3 -m idemcore_verify samples        # same as: make verify  or  sh verify_samples.sh

# 4. check one pair yourself: x86-64 CPU vs NVIDIA L40S, gpt-oss-20b
python3 -m idemcore_verify compare samples/gpt-oss-20b/x86_64.log \
                                   samples/gpt-oss-20b/nvidia_l40s.log

# 5. the unit tests, including a tamper test
python3 -m unittest discover -s tests
```

Expected output of step 3:

```
checked 65 logs (448904 token rows) and 58 pairs
PASS: every published hash recomputes and every pair is bit-identical
```

and of step 4:

```
OK   samples/gpt-oss-20b/x86_64.log: 512 tokens, ALL 8ec348aaf3b4109c (recomputed 8ec348aaf3b4109c)
OK   samples/gpt-oss-20b/nvidia_l40s.log: 512 tokens, ALL 8ec348aaf3b4109c (recomputed 8ec348aaf3b4109c)
MATCH: 512/512 positions identical (mode exact; only-in-ref 0, only-in-cand 0)
```

Step 3 recomputes all 65 published digests in
[samples/HASHES.tsv](samples/HASHES.tsv) from the shipped logs (about 450 000
token rows, including batched GPU logs) and re-checks all 58 pairs in
[samples/PAIRS.tsv](samples/PAIRS.tsv). To prove the check is not a rubber
stamp, edit any hex digit in a log and run it again: the chain breaks.

`idemcore-verify samples` looks for `./samples` in the current directory; run
it from the repository root, or pass `--dir path/to/samples`. `make` is not
required; every `make` target is a one-line Python command.

### Check a live answer from api.idemcore.net

The hosted API (`https://api.idemcore.net/v1`, OpenAI-compatible) attaches a
receipt to every answer, and `GET /v1/receipts/{id}/log` returns that answer's
per-token log. The API serves the public form of the log (`log_format`
`idemcore-log/r1-public`): the `pi j h hc` fields of [SPEC.md](SPEC.md) plus the
`ALL` line, without `freq` and `total`. The verifier accepts both forms (version
0.3.0 and later). Access needs an API key: sign in to the console at
<https://console.idemcore.net/#/login> and create one. With a key, save the log and run:

```sh
curl -s https://api.idemcore.net/v1/receipts/RECEIPT_ID/log \
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

All hash tables, per device, workload and batch size: [EVIDENCE.md](EVIDENCE.md).

Requires Python ≥ 3.9, standard library only.

## What the verifier checks

1. **Well-formedness** – every line has six fields, hashes are 64-bit hex,
   `0 < freq ≤ total < 2^31`, no duplicate positions.
2. **Chain integrity** – it recomputes the `ALL` digest from the per-token
   lines; editing a single line breaks it.
3. **Agreement** – it compares a candidate log against a reference log
   position by position, keyed by `(payload, position)`, and prints the first
   divergence (which token, which field). `--subset` allows a short spot check
   (e.g. 128 CPU tokens against a 512-token GPU run).

A match on `h` means the two machines computed the **same integer logits for
the whole vocabulary** at that position, not just the same argmax token. A
match on `hc` means they built the same integer sampling distribution, so any
seeded sampler driven by it makes the same choices.

## Published pairs

| Model | Reference | Candidate | Positions | Result |
|---|---|---|---|---|
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | NVIDIA T4 | 3260 | identical |
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | Galaxy Z Fold5 (Android) | 240 | identical |
| Qwen2.5-0.5B, 8-bit | x86-64 CPU | Windows 11 ARM64 laptop (Snapdragon X Plus) | 240 | identical |
| Qwen2.5-7B, 8-bit | x86-64 CPU | NVIDIA A10 | 512 | identical |
| Qwen2.5-7B, 8-bit | x86-64 CPU | Galaxy Z Fold5 (Android) | 64 (prefix) | identical |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | NVIDIA A10 | 512 | identical |
| Qwen2.5-7B, 4-bit (g4) | x86-64 CPU | NVIDIA A10G | 512 | identical |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | Galaxy Z Fold5 (Android), both CPU code paths | 128 (prefix) | identical |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | x86-64 CPU, 6 repeat runs (6 and 8 pinned threads) | 512 | identical |
| Qwen2.5-7B, 4-bit (g) | x86-64 CPU | NVIDIA A10G and A10, batched B = 1–64, shuffled and staggered (40 logs) | every row of every stream | identical |
| gpt-oss-20b (MoE) | x86-64 CPU | NVIDIA L40S | 512 | identical |
| gpt-oss-120b (MoE) | x86-64 CPU (spot check) | NVIDIA H100 | 128 of 512 | identical |

Details per file: [samples/MANIFEST.md](samples/MANIFEST.md).
Qwen2.5-7B 4-bit on Android runs at 3.39 tok/s on the Fold5 (see [RESULTS.md](RESULTS.md)).

**Batched GPU serving.** With an improved batched GPU kernel, Qwen2.5-7B 4-bit
on an NVIDIA A10G serves up to 64 concurrent streams, and every stream's
per-token hashes match a single-stream x86-64 run at batch sizes 1, 8, 16, 32
and 64, including shuffled slot order and staggered joins (0 mismatches).
The same holds on an NVIDIA A10. Aggregate throughput (A10G): 641 tok/s at 8
streams and 1372 tok/s at 32. Numbers and caveats:
[RESULTS.md](RESULTS.md#2b-batched-serving-qwen25-7b-4-bit-g-nvidia-a10g).
The raw batched logs are in `samples/batched/` and are re-checked by step 3 above.

## Methodology and benchmarks

* How every number was measured (workloads, clocks, baselines, energy,
  quality): [METHODOLOGY.md](METHODOLOGY.md).
* Results and their caveats: [RESULTS.md](RESULTS.md); every hash, per device,
  workload and batch size: [EVIDENCE.md](EVIDENCE.md).
* The serving-benchmark kit used in the paper will be published separately and
  linked here.

## Paper

Don Wick, *Idemcore: Bit-Identical LLM Inference from Phones to Datacenter
GPUs, with an Open Per-Token Verification Protocol*, preprint, Zenodo,
2026. DOI: [10.5281/zenodo.23851129](https://doi.org/10.5281/zenodo.23851129).
Citation metadata: [CITATION.cff](CITATION.cff).

## What this does **not** prove

* The logs are produced by our engine. A matching pair shows two runs agree;
  it does not prove *which* program produced them. To check a provider, re-run
  the same request on hardware you control (or ask a second party to) and
  compare logs.
* The hash is FNV-1a-64: fast and good for detecting accidental divergence,
  **not** collision-resistant against an adversary who can choose logits. A
  SHA-256 / BLAKE3 variant of the log is planned; the format has a version.

## License

Apache-2.0 for everything in this repository (verifier, spec, methodology,
sample logs). See [LICENSE](LICENSE). Idemcore's inference kernel, weight
format, and tables are proprietary and are not covered by this license.

Contact: Don Wick — don.wick@idemcore.net · Website: <https://idemcore.net>
· Security reports: [SECURITY.md](SECURITY.md) · Mismatch reports: open an
issue with the "Hash mismatch" template.

Copyright 2026 Don Wick.
