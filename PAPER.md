# Empty Is Not Unreachable

### Four states a web-reading agent needs, and what happens in the twenty-eight sources that only have two

**Gokul Sai** · Hyderabad, India · Independent
Version 2, 16 September 2026
DOI: [10.5281/zenodo.22828298](https://doi.org/10.5281/zenodo.22828298)

---

## Abstract

A program asked whether a restaurant has a Google listing. Google answered with
an HTTP 200 whose body said `REQUEST_DENIED`, and the program wrote *this
restaurant has no Google listing* about a restaurant that has one. The refusal
arrived inside the envelope of a successful answer, and the only software
positioned to notice threw the evidence away.

Agents that read the web report what they found. Most cannot report what they
failed to find out. A source that answers with nothing and a source that never
answers at all collapse into the same empty list.

I probed 28 public web sources used for finding student opportunities in India
and classified each into four states rather than two: answered with content,
answered with nothing, answered with a refusal, and did not answer. Thirteen
were live, three served only records years out of date, eleven returned no
structured content, and one was unreachable. A two-state reader records that as
16 hits and 12 misses, and is wrong about four of the sixteen and about the one
it cannot tell apart from the twelve.

Three further arms test the survey rather than repeat it. Repeating the whole
probe four days later returned identical counts. Running the same classifier
over 12 non-Indian sources produced a similar empty rate, which weakens the
India-specific reading. Opening six of the eleven empty sources in a real
browser showed that JavaScript rendering does not rescue them: the listings
appear as text, and the structured data the classifier asks for is absent both
before and after rendering.

Four distinct failure shapes appeared, each of which a two-state reader records
as an ordinary empty result. The fourth was found while checking a link for this
paper. Two occurred inside programs written specifically to prevent them,
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

In code the contract costs four lines. What matters is that the failure branch
cannot produce the same value as the empty branch:

```python
def read(url):
    try:
        text = fetch(url)
    except Exception as exc:
        return ERROR, type(exc).__name__, []   # nothing was learned
    items = parse(text)
    if not items:
        return EMPTY, "answered, nothing of the kind asked for", []
    return OK, "%d found" % len(items), items
```

A caller that unpacks the state cannot silently treat the first case as the
second. A caller that receives only `items` always can.

## 3. Method

Twenty-eight public sources were probed once each on 12 September 2026 from a
residential connection in Hyderabad: event platforms, hackathon platforms,
Indian scholarship portals, and internship boards. The full list is in
`check_sources.py`, which is the survey. Each source was fetched over HTTPS with
a descriptive user-agent and a 25-second timeout. No API keys, no logins and no
browser engine, because the question was what a keyless agent reading raw HTML
can learn.

Classification used structured data present in the returned HTML
(`schema.org` JSON-LD) and, where events were found, the dates attached to them.
A transport failure produced `ERROR` and no further analysis.

Three further arms were added on 16 September 2026, each aimed at a specific
weakness of the first survey rather than at more sources of the same kind:

1. **Repeat.** The identical probe was re-run four days later, to separate
   transient failures from stable ones.
2. **Geography.** The same classifier was run over 12 non-Indian sources of the
   same four kinds, in `check_global.py`, to test whether the empty rate is a
   property of Indian portals or of the method.
3. **Rendering.** Six of the eleven `EMPTY` sources were opened in a real
   browser with JavaScript enabled, and their structured data was read from the
   live DOM, to test the claim that the content exists but not in the HTML.

Both scripts carry six assertions each, written from cases actually observed,
and each verified to fail when the logic it guards is broken.

## 4. Results

Twenty-eight Indian-facing sources, probed twice:

| State | 12 Sept | 16 Sept | |
|---|---|---|---|
| **OK** | 13 | 13 | structured, dated, ahead |
| **EMPTY** | 11 | 11 | answered, nothing structured in the HTML |
| **STALE** | 3 | 3 | answered, content, all of it expired |
| **ERROR** | 1 | 1 | never answered |

The second run is not merely the same totals. The same three Luma city pages
were stale, with the same newest records of 2022-08-15, 2021-12-12 and
2021-12-26, and the same government scholarship portal was unreachable both
times. The one `ERROR` is therefore a standing property of that source over at
least four days, not a blip on the evening of the survey.

A two-state reader records this as **16 hits and 12 misses**, and is wrong about
four of the sixteen and about the one it cannot distinguish from the twelve.

### The same classifier on 12 non-Indian sources

| State | Sources | |
|---|---|---|
| **OK** | 7 | Luma SF, NYC and London; Meetup Austin, London, Berlin; Eventbrite SF |
| **EMPTY** | 4 | Devpost, MLH, scholarships.com, Fastweb |
| **STALE** | 0 | |
| **ERROR** | 1 | Wellfound internships, HTTP 404 |

The empty rate is 4 of 12 outside India against 11 of 28 inside it, which is
33% against 39%. Version 1 predicted that the Indian composition inflates
`EMPTY`, and the direction of that prediction holds. The size does not: six
percentage points across 40 hand-picked sources is well inside what a sample
this small can produce by chance. Client-rendered listing pages are not an
Indian phenomenon, and neither is the failure this paper is about.

The non-Indian arm also produced a second shape of `ERROR`: an HTTP 404 rather
than a connection failure. Both mean nothing was learned, and both are reported
as `ERROR`, but only one of them would look like an outage to a person watching.

### What is actually in the empty sources, after JavaScript runs

| Source | JSON-LD blocks after render | Types present | `Event` | Visible text |
|---|---|---|---|---|
| internshala | 4 | FAQPage, BreadcrumbList, ItemList, SoftwareApplication | 0 | 59,459 chars |
| buddy4study | 2 | WebSite, EducationalOrganization | 0 | 27,100 chars |
| devpost | 1 | WebSite | 0 | 2,214 chars |
| unstop | 0 | none | 0 | 4,194 chars |
| devfolio | 0 | none | 0 | 2,535 chars |
| luma/hyderabad | 0 | none | 0 | 1,596 chars |

This corrects the first version of this paper, which said the eleven empty
results were client-rendered pages whose content exists but not in the HTML.
Half of that is right and half is wrong. The listings do exist once JavaScript
runs: internshala renders 59,459 characters of text across 528 links. The
structured data does not. Not one of the six publishes a `schema.org` `Event`
either before or after rendering, and internshala, an internship board, does not
publish `JobPosting` either.

So `EMPTY` here does not mean "rendered client-side". It means the source does
not publish machine-readable records of the kind asked for, at any point in its
lifecycle. That is a stronger finding than the one it replaces, and a worse one
for anyone planning to read these sites without a browser.

## 5. Four shapes of silent failure

A non-zero count that is four years old. Three pages returned events. Their
newest records were dated 2022-08-15, 2021-12-12 and 2021-12-26, on both runs.
The most dangerous of the three sits at a URL that reads like a national feed,
so a collector asking *does this have events?* adds an entire country to its
coverage map on the strength of one expired record. The test is not "has
content" but "has content that is still valid," and the two are easy to conflate
because the first is trivial to compute.

Structured data that is furniture. One internship board returned 514 KB
containing four JSON-LD blocks, a promising signal until inspection showed they
described breadcrumbs and an FAQ accordion. The browser arm names them exactly:
FAQPage, BreadcrumbList, ItemList and SoftwareApplication. Zero listings.
Counting structured-data blocks measures a site's SEO configuration, not its
content.

A fallback page that is not a 404. A city page for a city the platform does
not cover returned 206,299 bytes. This was not an error page but the platform's
generic discovery page. A made-up city name at the same URL shape returned
27,762 bytes. Opened in a browser, that same city URL renders the platform's
generic discovery page, titled *Discover Events*, with no structured data at
all. The absence of a 404 is not evidence that the requested thing exists; the
size comparison against a deliberately invalid request is what revealed it.

A status code that disagrees with the page. The fourth shape turned up while
checking a link for this paper, on the author's own site. On 16 September 2026
the journal entry cited in §6 was fetched two ways within the same minute. Over
HTTPS it returned **HTTP 404**, 770 bytes, and the word `firstwrong` zero times.
In a browser the same URL rendered 5,717 characters of that entry. The site is a
client-rendered application on GitHub Pages, which serves its 404 shell for any
path it does not recognise and lets the client router find the page. A keyless
reader records `ERROR`. A person records a working link. Neither is misreading
the transport; they are reading two different answers to the same request, and
an agent that only has two states will file this page next to a server that is
down.

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

A third case belongs to this paper rather than to the code. Version 1 reported
that the eleven empty sources were client-rendered pages whose content exists
but not in the HTML. The classifier had never checked that, and §4 shows it is
wrong: the content renders, the structured data never exists. The state machine
was right again, and the explanation attached to it was a guess wearing the
clothes of a measurement.

This is not the first time. On 9 September 2026 the author reviewed his own
repositories and found the same shape in five of them in one afternoon, written
up at the time in a journal entry called *The bug was in the tool I built to
find the bug*:

- `firstwrong` tells a student the first line of their working that is wrong.
  When the model's reply could not be read, it printed **"No wrong line found."**
  That is a pass. The tool told the student their work was fine because it could
  not read the answer, which is the exact failure the tool exists to prevent.
- `apisurface` reports what an npm package removed between versions. It printed
  **"0 changes, this is a real zero"** for `@types/node` while having read 1 file
  out of 89. It was right about the file it read and wrong about how many there
  were.
- `skillcheck` counts which installed tools have ever been used. When the folder
  it scans was missing or unreadable it printed **"60 skills installed, 0 ever
  used, across 0 sessions"** and exited 0, which is byte for byte what it prints
  on a machine that genuinely never used one.
- `mdwatch` watches a workspace and reports what needs attention. A byte order
  mark at the front of `tasks.json` broke the parse, so it printed **"No open
  tasks."** with a task sitting at blocked inside that file.
- `synth` summarises a paper with a page number on every claim. Its page reader
  returned nothing both for a blank page in the middle and for a page past the
  end, so a paper with a blank page four became a three page paper, and the tool
  then accused the model of citing pages that do not exist.

Five for five. Every tool the author had written that reads something and
reports a count carried the same bug, in code written by someone who had already
written the rule down.

A four-state contract protects only the layer that implements it. Every boundary
downstream, whether a temp file, a log line, a sentence or a paper, can silently
collapse the states again.

## 7. The contract

1. Never let a transport failure produce the same value as an empty result.
2. Treat a refusal as its own state, and check the body for one even when the
   status code says success.
3. Validate that content is current, not merely present.
4. Verify that structured data contains the entity you asked for.
5. Compare against a deliberately invalid request to detect fallback pages.
6. Carry the distinction all the way into the prose the user reads.

## 8. Limitations

This is a single-observer study. Forty sources were probed in total, 28 Indian
and 12 not, over two runs four days apart, from one network, with one classifier
written by the person reporting the results. Repetition removes the "one
evening" objection and the non-Indian arm removes the "one country" objection.
Neither removes the observer.

The gap that remains is a second rater. Every state in every table was assigned
by one program written by one person, and where the program was ambiguous the
same person resolved it. An independent classification of the same 40 sources by
someone with no stake in the result, reported as an agreement rate, would turn
these counts into a measurement rather than a report. That has not been done.

Forty sources is still a small sample, chosen by hand rather than drawn at
random, so the proportions here describe these sources and not the web. The
browser arm covers 6 of the 11 empty sources, not all of them.

No claim is made that the four states are complete. `STALE` was not anticipated
and had to be added mid-survey, which is itself weak evidence that others remain.

## 9. Reproduction

Both scripts re-run their probes and print the tables in §4. Results will differ
from those reported here, because the sources change, and shipping the scripts
rather than only the tables is what makes that visible.

```
py -3 check_sources.py --check    the six assertions
py -3 check_sources.py            the 28-source survey
py -3 check_global.py --check     the six assertions
py -3 check_global.py             the 12 non-Indian sources
```

The browser arm was run by hand against the live sites and is reported in §4;
its numbers are the ones a browser console returns for the JSON-LD blocks and
visible text on each page.

---

*Corrections welcome. If a source is misclassified here, the script that
misclassified it is in this repository and the fix is a pull request.*

---

**Cite as:** Gokul Sai (2026). *Empty Is Not Unreachable: four states a
web-reading agent needs, and what happens in the twenty-eight sources that only
have two.* Zenodo. https://doi.org/10.5281/zenodo.22828298
