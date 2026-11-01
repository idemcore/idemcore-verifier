PY ?= python3

.PHONY: verify verify-verbose test
verify:            ## recompute every published hash from samples/ and print PASS/FAIL
	$(PY) -m idemcore_verify samples

verify-verbose:
	$(PY) -m idemcore_verify samples -v

test:
	$(PY) -m unittest discover -s tests -v
