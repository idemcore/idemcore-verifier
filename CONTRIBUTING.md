# Contributing

This repository covers the Idemcore **log format** and the **open verifier**
only: the spec, the Python checker, the methodology notes and the sample logs.

The Idemcore inference engine and its model files are not open
source and is not part of this repository. Pull requests that try to add,
reimplement or change the engine will not be accepted.

Welcome:

* **Mismatch reports.** If two runs of the same model and input give
  different hashes, please open an issue with the "Hash mismatch" template and
  attach both logs (or their `ALL` values), the verifier output and the command.
* Bug fixes and tests for the verifier, and clarifications to `SPEC.md`.
* Logs from other engines that emit the same format.

Please keep the verifier dependency-free (Python standard library only) and
run `make verify` (or `python3 -m idemcore_verify samples`) and `python3 -m unittest discover -s tests` before
opening a pull request.

Questions about pilots or licensing the engine are out of scope for this
repository; please use <https://idemcore.net/#access> instead.
