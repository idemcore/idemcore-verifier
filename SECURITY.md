# Security policy

## Scope

This repository contains the Idemcore hash-log format (SPEC.md), the Python
verifier (`idemcore_verify/`) and sample logs. Please report privately:

* a way to make the verifier accept a log whose `ALL` or `STREAMS` digest does
  not match its lines, or to report `MATCH` for logs that differ;
* a crash, hang or excessive resource use caused by a crafted log file;
* a weakness in the log format beyond the known limitation below.

**Known limitation (not a vulnerability):** the format v1 hash is FNV-1a-64.
It detects accidental divergence but is not collision-resistant against an
adversary who can choose logits. A SHA-256 / BLAKE3 variant is planned.

A hash mismatch between two honest runs is a correctness report, not a
security issue: please open a public issue with the "Hash mismatch" template.

## How to report

Email **don.wick@idemcore.net** with the subject `SECURITY: idemcore-verifier`,
or use GitHub's private vulnerability reporting ("Report a vulnerability" on
the Security tab) if it is enabled. Include the affected version
(`python3 -m idemcore_verify --version`), a minimal log that reproduces the
problem and the command you ran.

We aim to acknowledge reports within 3 working days and to agree a disclosure
date with you. Please do not open a public issue for a security report.

## Supported versions

Only the latest release of the verifier receives fixes.
