"""Re-measure every source in docs/SOURCES.md, so that file never has to be
trusted on faith.

A project about things going stale cannot keep a stale list of where its data
comes from. Run this before believing the doc.

    py -3 check_sources.py            measure everything
    py -3 check_sources.py --check    run the self-checks only

Four verdicts, never two, because they are not the same fact:

    LIVE     answered, structured events, at least one dated in the future
    STALE    answered, events, but every one is in the past
    EMPTY    answered, nothing structured in the HTML (usually client rendered)
    ERROR    could not reach it, so we know nothing either way
"""

import datetime
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "opportunity-agent/0.1 (+research; gokulsai1004@gmail.com)")
TIMEOUT = 25

LIVE, STALE, EMPTY, ERROR = "LIVE", "STALE", "EMPTY", "ERROR"
MARK = {LIVE: " LIVE  ", STALE: " STALE ", EMPTY: " EMPTY ", ERROR: " ERROR "}

EVENT = re.compile(r'"@type"\s*:\s*"Event"')
DATE = re.compile(r'"(?:startDate|dateTime)"\s*:\s*"(\d{4}-\d{2}-\d{2})')

LUMA_CITIES = ["bangalore", "delhi", "mumbai", "indore", "hyderabad", "pune",
               "chennai", "kolkata", "india", "noida", "goa"]
LUMA_COMMUNITIES = ["spacexai-community", "deepmind", "design"]
MEETUP_CITIES = ["Bengaluru", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai"]
NO_STRUCTURE = [
    ("luma topic: ai", "https://luma.com/ai?k=t"),
    ("devfolio", "https://devfolio.co/hackathons"),
    ("devpost", "https://devpost.com/hackathons"),
    ("unstop", "https://unstop.com/competitions"),
    ("internshala", "https://internshala.com/internships"),
    ("buddy4study", "https://www.buddy4study.com/scholarships"),
    ("scholarships.gov.in", "https://scholarships.gov.in"),
    ("vidyalakshmi", "https://www.vidyalakshmi.co.in/"),
]


def body(url):
    """Returns (text, problem). Never returns a previous call's body: the
    first probe script reused a temp file, so a host that failed to connect
    was measured against the last page that worked and reported 313 KB of
    content it had never seen. A transport failure must produce nothing."""
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en-IN,en"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read().decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as exc:
        return "", "HTTP %d" % exc.code
    except Exception as exc:
        return "", "%s" % type(exc).__name__


def verdict(text, problem, today=None):
    """One source, one word, plus what it was based on.

    `today` is injectable so the future-date rule can be tested without
    waiting for the calendar.
    """
    if problem:
        return ERROR, problem, 0
    today = today or datetime.date.today().isoformat()
    events = len(EVENT.findall(text))
    dates = sorted(DATE.findall(text))
    if not events and not dates:
        return EMPTY, "nothing structured in the HTML", 0
    ahead = [d for d in dates if d >= today]
    if not ahead:
        # lu.ma/india serves one event from 2022 and looks exactly like the
        # national feed you want. A count above zero is not coverage.
        return STALE, "newest is %s, all in the past" % (dates[-1] if dates
                                                         else "unknown"), events
    return LIVE, "%d ahead, next %s, last %s" % (len(ahead), ahead[0],
                                                 ahead[-1]), events


def run():
    rows = []
    for city in LUMA_CITIES:
        rows.append(("luma/" + city, "https://luma.com/%s" % city))
    for slug in LUMA_COMMUNITIES:
        rows.append(("luma~" + slug[:14], "https://luma.com/%s?k=c" % slug))
    for city in MEETUP_CITIES:
        rows.append(("meetup/" + city,
                     "https://www.meetup.com/find/?location=in--%s&source=EVENTS"
                     % city))
    rows.extend(NO_STRUCTURE)

    counts = {LIVE: 0, STALE: 0, EMPTY: 0, ERROR: 0}
    print()
    for name, url in rows:
        text, problem = body(url)
        state, why, events = verdict(text, problem)
        counts[state] += 1
        print("  %s %-22s %-3s  %s" % (MARK[state], name,
                                       events or "-", why))
    print("\n  %d live, %d stale, %d empty, %d unreachable\n"
          % (counts[LIVE], counts[STALE], counts[EMPTY], counts[ERROR]))
    return counts


def check():
    """Each case is one that actually came back on 12 Sept 2026."""
    today = "2026-09-12"
    live = '"@type":"Event" "startDate":"2026-09-24T10:00:00.000+05:30"'
    assert verdict(live, "", today)[0] == LIVE
    # lu.ma/india: one event, from 2022. A count above zero is not coverage.
    old = '"@type":"Event" "startDate":"2022-08-15T10:00:00.000+05:30"'
    assert verdict(old, "", today)[0] == STALE
    # A client-rendered page answers 200 with no structure in it.
    assert verdict("<html>lots of javascript</html>", "", today)[0] == EMPTY
    # The one the first script got wrong: unreachable is not empty.
    assert verdict("", "URLError", today)[0] == ERROR
    assert verdict("", "URLError", today)[0] != verdict("", "", today)[0]
    # An event exactly today still counts as ahead; it has not happened yet.
    assert verdict('"startDate":"2026-09-12T23:00:00+05:30"', "", today)[0] == LIVE
    print("  6 checks pass")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        check()
        run()
