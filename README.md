# Empty Is Not Unreachable

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22828298.svg)](https://doi.org/10.5281/zenodo.22828298)

A web-reading agent needs four states, not two. **Nothing was there** is a
result. **I could not look** is not. A program that prints them the same way
lies exactly when it has failed.

The four states are `LIVE`, `STALE`, `EMPTY`, and `ERROR`. `EMPTY` means the
page answered with nothing structured in it. `ERROR` means it could not be
reached, so nothing is known either way. Collapsing those two is the failure
this repo is about, and two of the four found in the paper were inside programs
written to prevent it.

`PAPER.md` is the write-up: 40 public sources probed, 28 Indian-facing and 12
not, over two runs four days apart, plus a browser arm.

## What it is not

- Not a scraper. It classifies whether a source is live, stale, empty, or
  unreachable; it does not pull the events out.
- Not a fixed dataset. Results differ from the tables in the paper because the
  sources change. That is why the scripts ship, not just the numbers.
- Not independently rated. See the known gap below.

## Run it yourself

```
py -3 check_sources.py --check    six self-checks
py -3 check_sources.py            the 28-source survey
py -3 check_global.py --check     six self-checks
py -3 check_global.py             the 12 non-Indian sources
```

No API keys, no logins, no browser engine. Standard library only.
`check_global.py` imports the same `verdict()` rather than copying it, so the
two arms are graded by one rule.

## Known gap

One observer. Every state was assigned by one classifier written by the person
reporting the results. An independent rating of the same 40 sources, reported as
an agreement rate, is what would turn this into a measurement. Corrections and
pull requests welcome.

## Cite

`CITATION.cff` has the full entry. DOI: [10.5281/zenodo.22828298](https://doi.org/10.5281/zenodo.22828298).
