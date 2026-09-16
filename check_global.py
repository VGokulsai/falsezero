"""Does the four-state picture hold outside India?

The first survey was 28 Indian-facing sources, and its own limitations section
says that skew probably inflates EMPTY: Indian scholarship and internship
portals are heavily client-rendered. This probes non-Indian sources of the same
kinds, with the same classifier, so that caveat becomes a measurement instead of
a guess.

    py -3 check_global.py            measure everything
    py -3 check_global.py --check    the self-checks only

Same verdict() as check_sources.py, imported rather than copied: two copies of a
classifier drift, and then the comparison is between two different rules.
"""

import sys

from check_sources import EMPTY, ERROR, LIVE, MARK, STALE, body, verdict

# Same four kinds as the Indian survey: event platforms, hackathon platforms,
# scholarship portals, internship boards. Cities chosen to be where each
# platform is strongest, so a thin result is about the platform, not the city.
SOURCES = [
    ("luma/sf",            "https://luma.com/sf"),
    ("luma/nyc",           "https://luma.com/nyc"),
    ("luma/london",        "https://luma.com/london"),
    ("meetup/Austin",      "https://www.meetup.com/find/?location=us--tx--Austin&source=EVENTS"),
    ("meetup/London",      "https://www.meetup.com/find/?location=gb--London&source=EVENTS"),
    ("meetup/Berlin",      "https://www.meetup.com/find/?location=de--Berlin&source=EVENTS"),
    ("eventbrite/sf",      "https://www.eventbrite.com/d/ca--san-francisco/events/"),
    ("devpost",            "https://devpost.com/hackathons"),
    ("mlh",                "https://mlh.io/seasons/2026/events"),
    ("scholarships.com",   "https://www.scholarships.com/financial-aid/college-scholarships"),
    ("fastweb",            "https://www.fastweb.com/college-scholarships"),
    ("wellfound interns",  "https://wellfound.com/role/internship"),
]


def run():
    counts = {LIVE: 0, STALE: 0, EMPTY: 0, ERROR: 0}
    print()
    for name, url in SOURCES:
        text, problem = body(url)
        state, why, events = verdict(text, problem)
        counts[state] += 1
        print("  %s %-20s %-3s  %s" % (MARK[state], name, events or "-", why))
    print("\n  %d live, %d stale, %d empty, %d unreachable  (of %d)\n"
          % (counts[LIVE], counts[STALE], counts[EMPTY], counts[ERROR],
             len(SOURCES)))
    return counts


def check():
    """The classifier is the imported one, so these check that this file uses
    it unchanged rather than re-testing its rules."""
    today = "2026-09-16"
    assert verdict('"@type":"Event" "startDate":"2026-12-01T10:00:00Z"', "", today)[0] == LIVE
    assert verdict('"startDate":"2019-01-01T10:00:00Z"', "", today)[0] == STALE
    assert verdict("<html>js only</html>", "", today)[0] == EMPTY
    # The distinction the whole paper is about, asserted here too because this
    # file is what the geography claim will rest on.
    assert verdict("", "URLError", today)[0] == ERROR
    assert verdict("", "URLError", today)[0] != verdict("<html>js</html>", "", today)[0]
    # No Indian source may sit in this list, or the comparison means nothing.
    assert not [u for _n, u in SOURCES if "in--" in u or ".in/" in u or u.endswith(".in")], \
        "this list is the non-Indian arm"
    print("  6 checks pass")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        check()
        run()
