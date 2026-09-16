# Empty Is Not Unreachable

A web-reading agent needs four states, not two. **Nothing was there** is a
result. **I could not look** is not. A program that prints them the same way
lies exactly when it has failed.

`PAPER.md` is the write-up: 40 public sources probed, 28 Indian and 12 not,
over two runs four days apart, plus a browser arm. Four shapes of silent
failure, two of them found inside programs written to prevent them.

## Run it yourself

```
py -3 check_sources.py --check    the six assertions
py -3 check_sources.py            the 28-source survey
py -3 check_global.py --check     the six assertions
py -3 check_global.py             the 12 non-Indian sources
```

No API keys, no logins, no browser engine, standard library only. Results will
differ from the tables in the paper, because the sources change. That is why
the scripts ship and not just the numbers.

## Known gap

One observer. Every state was assigned by one classifier written by the person
reporting the results. An independent rating of the same 40 sources, reported
as an agreement rate, is what would turn this into a measurement. Corrections
and pull requests welcome.
