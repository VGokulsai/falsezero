# Empty Is Not Unreachable

### Four states a web-reading agent needs, and what happens in the twenty-eight sources that only have two

**Gokul Sai** · Hyderabad, India · Independent
Draft, 13 September 2026

---

## Abstract

Agents that read the web report what they found. Most of them cannot report what
they failed to find out. A source that answers with nothing and a source that
never answers at all collapse into the same empty list, and the agent goes on to
make a confident claim on top of it.

I probed 28 public web sources used for finding student opportunities in India
and classified each into four states rather than two: answered with content,
answered with nothing, answered with a refusal, and did not answer. Thirteen
were live, three served only records years out of date, eleven returned no
structured content, and one was unreachable. Three distinct failure shapes
appeared, each of which a two-state reader records as an ordinary empty result.
Two of them occurred inside programs written specifically to prevent them,
including one written on the day of the survey by the author.

The contribution is a contract: six rules, and the finding that they are hard to
keep even when you already know about them.

---

## 1. A refusal that looks like an answer

Asked for a business in Hyderabad, the Google Places text search API returns
this:

```
HTTP/1.1 200 OK

{
  "status": "REQUEST_DENIED",
  "results": [],
  "error_message": "You must use an API key to authenticate each request..."
}
```

The transport succeeded. The status code is 200. The `results` array is empty.

A caller that checks `response.ok` and reads `results` concludes that Google has
never heard of the business. If that caller is generating a report for the
business owner, it writes *this restaurant has no Google listing* about a
restaurant with a Google listing.

Nothing failed loudly. No exception was raised, no retry was triggered and no
log line was written, so the one piece of software positioned to notice the
refusal threw the evidence away instead.

## 2. Four states, not two

The states are distinguished by two questions: did the source answer, and did
the answer contain what was asked for.

| State | Answered? | Content? | What it means |
|---|---|---|---|
| **OK** | yes | yes | The thing is there. |
| **EMPTY** | yes | no | The thing is genuinely not there. **A finding.** |
| **BLOCKED** | yes | refused | A key, a login, or a payment method is missing. |
| **ERROR** | no | — | Nothing was learned. **Not a finding.** |

`EMPTY` is a result you can publish. `ERROR` is not: it is the absence of a
measurement, and reporting it as `EMPTY` converts ignorance into a claim.

`BLOCKED` deserves its own state rather than folding into `ERROR` because it is
actionable in a way `ERROR` is not, and because, as §1 shows, it frequently
arrives wearing a success code.

A fifth state, **STALE**, emerged during the survey and is discussed in §5.

## 3. Method

Twenty-eight public sources were probed once each on 12 September 2026 from a
residential connection in Hyderabad: event platforms, hackathon platforms,
Indian scholarship portals, and internship boards. Each was fetched over HTTPS
with a descriptive user-agent and a 25-second timeout. No API keys, no logins
and no browser engine, because the question was what a keyless agent reading raw
HTML can learn.

Classification used structured data present in the returned HTML
(`schema.org` JSON-LD) and, where events were found, the dates attached to them.
A transport failure produced `ERROR` and no further analysis.

The probe is `check_sources.py`, included here. It carries six assertions, each
written from a case actually observed, and each verified to fail when the logic
it guards is broken.

## 4. Results

| State | Sources | |
|---|---|---|
| **OK** | 13 | structured, dated, ahead |
| **EMPTY** | 11 | answered, nothing structured in the HTML |
| **STALE** | 3 | answered, content, all of it expired |
| **ERROR** | 1 | never answered |

A two-state reader records this as **16 hits and 12 misses**, and is wrong about
four of the sixteen and about the one it cannot distinguish from the twelve.

The eleven `EMPTY` results are almost entirely client-rendered applications:
the content exists, but not in the HTML. That is a genuine finding for a keyless
reader and a false one for any reader who concludes the data does not exist.

## 5. Three shapes of silent failure

A non-zero count that is four years old. Three pages returned events. Their
newest records were dated 2022-08-15, 2021-12-12 and 2021-12-26. The most
dangerous of the three sits at a URL that reads like a national feed, so a
collector asking *does this have events?* adds an entire country to its coverage
map on the strength of one expired record. The test is not "has content" but
"has content that is still valid," and the two are easy to conflate because the
first is trivial to compute.

Structured data that is furniture. One internship board returned 514 KB
containing four JSON-LD blocks, a promising signal until inspection showed they
described breadcrumbs and an FAQ accordion. Zero listings. Counting
structured-data blocks measures a site's SEO configuration, not its content.

A fallback page that is not a 404. A city page for a city the platform does
not cover returned 206,299 bytes. This was not an error page but the platform's
generic discovery page. A made-up city name at the same URL shape returned
27,762 bytes. The absence of a 404 is not evidence that the requested thing
exists; the size comparison against a deliberately invalid request is what
revealed it.

## 6. The instrument catches the disease

The strongest evidence that this class is hard to design out is that it occurred
twice during this work, in code written to prevent it.

Case one. The first version of the probe used a single temporary file for
every response body and did not clear it between requests. When a host failed to
connect, `curl` wrote nothing, and the classifier measured the *previous*
source's body. The run reported that an unreachable government portal had
returned 313 KB of richly structured content. The numbers were real; they
belonged to a different website. The fix is one line, truncating the file before
every fetch, and the bug had already produced a table that was about to be
believed.

Case two. Later the same evening, a source-availability checker printed
`no website listed anywhere — which is itself a finding` for a business operating
a large commercial website. The four states were computed correctly. The sentence
rendering them claimed more than the data supported: what the program knew was
that one open database had no `website` tag. The state machine was right and the
English was wrong, which is the same bug relocated into the reporting layer.

On 9 September 2026 the author found this same class in five of his own
repositories at once, one of them `firstwrong`, a tool whose stated purpose is
locating the first point at which a process goes wrong.

A four-state contract protects only the layer that implements it. Every boundary
downstream, whether a temp file, a log line or a sentence, can silently collapse
the states again.

## 7. The contract

1. Never let a transport failure produce the same value as an empty result.
2. Treat a refusal as its own state, and check the body for one even when the
   status code says success.
3. Validate that content is current, not merely present.
4. Verify that structured data contains the entity you asked for.
5. Compare against a deliberately invalid request to detect fallback pages.
6. Carry the distinction all the way into the prose the user reads.

## 8. Limitations

This is a single-observer survey of 28 sources, taken on one day, from one
country, over one network, without a browser engine, without repeated trials,
and without a second rater. It shows that the failure modes exist and are easy
to hit. It does not establish how common they are across the web, and the
proportions in §4 should not be read as prevalence.

The India-specific composition is deliberate but narrowing: Indian scholarship
and internship portals skew heavily toward client-rendered applications, which
likely inflates the `EMPTY` count relative to a broader sample.

No claim is made that the four states are complete. `STALE` was not anticipated
and had to be added mid-survey, which is itself weak evidence that others remain.

## 9. Reproduction

`check_sources.py` re-runs every probe and prints the table in §4. Results will
differ from those reported here, because the sources change, and shipping the
script rather than only the table is what makes that visible.

```
py -3 check_sources.py --check    the six assertions
py -3 check_sources.py            the full survey
```

---

*Corrections welcome. If a source is misclassified here, the script that
misclassified it is in this repository and the fix is a pull request.*
