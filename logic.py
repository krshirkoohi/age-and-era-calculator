"""Core calculation and helper utilities for Age & Era Calculator.
"""
from __future__ import annotations

import os
from datetime import date, datetime
from typing import Tuple

try:
    from openai import OpenAI # type: ignore
except ImportError:  # pragma: no cover
    OpenAI = None  # Placeholder so type checkers do not complain
    openai = None # for older references, will be cleaned up

# ---------------------------------------------------------------------------
# Pure calculations (no external services)
# ---------------------------------------------------------------------------

def parse_birthdate(*, age: int | None = None, dob: date | None = None) -> date:
    """Return a ``date`` object for the person's birth.

    The user may supply an *age* (integer years) **or** an explicit *dob*.
    ``ValueError`` is raised if neither (or both) are provided.
    """
    if dob is not None and age is not None:
        raise ValueError("Please specify either age or date of birth, not both.")

    if dob is not None:
        if dob > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return dob

    if age is not None:
        if not (0 < age < 130):
            raise ValueError("Age must be between 1 and 129.")
        today = date.today()
        # Attempt to keep month/day; fallback for 29 Feb edge-case.
        try:
            birth = date(today.year - age, today.month, today.day)
        except ValueError:  # 29 Feb when today is 29 Feb on non-leap year
            birth = date(today.year - age, today.month, today.day - 1)
        return birth

    raise ValueError("Please specify either age or date of birth.")


def compute_periods(birth: date) -> Tuple[date, date, date, date, date, date]:
    """Return (child_start, child_end, teen_start, teen_end, ya_start, ya_end).
    
    Childhood years: 5-12
    Teenage years: 13-19
    Young adult years: 20-29
    """
    child_start = birth.replace(year=birth.year + 5)
    child_end = birth.replace(year=birth.year + 12)
    teen_start = birth.replace(year=birth.year + 13)
    teen_end = birth.replace(year=birth.year + 19)
    ya_start = birth.replace(year=birth.year + 20)
    ya_end = birth.replace(year=birth.year + 29)
    return child_start, child_end, teen_start, teen_end, ya_start, ya_end


def decade_label(year: int) -> str:
    decade = (year // 10) * 10
    return f"{decade}s"


def get_generation(year: int) -> str:
    """Return a conventional Western generational label."""
    if 1928 <= year <= 1945:
        return "Silent Generation"
    if 1946 <= year <= 1964:
        return "Baby Boomer"
    if 1965 <= year <= 1980:
        return "Generation X"
    if 1981 <= year <= 1996:
        return "Millennial"
    if 1997 <= year <= 2012:
        return "Generation Z"
    if year >= 2013:
        return "Generation Alpha"
    return "Unknown"


def get_star_sign(birth: date) -> str:
    """Return the Western zodiac sign for *birth* date."""
    m, d = birth.month, birth.day
    if (m == 12 and d >= 22) or (m == 1 and d <= 19):
        return "Capricorn"
    if (m == 1 and d >= 20) or (m == 2 and d <= 18):
        return "Aquarius"
    if (m == 2 and d >= 19) or (m == 3 and d <= 20):
        return "Pisces"
    if (m == 3 and d >= 21) or (m == 4 and d <= 19):
        return "Aries"
    if (m == 4 and d >= 20) or (m == 5 and d <= 20):
        return "Taurus"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20):
        return "Gemini"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22):
        return "Cancer"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22):
        return "Leo"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22):
        return "Virgo"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22):
        return "Libra"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21):
        return "Scorpio"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21):
        return "Sagittarius"
    return "Unknown"

# ---------------------------------------------------------------------------
# LLM integration (optional)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a cultural historian. For an individual from {country}, provide a personalized cultural summary for the following periods: childhood ({child_start}-{child_end}), teenage years ({teen_start}-{teen_end}), and young adult years ({ya_start}-{ya_end}).\n\n"
    "Present the information using Markdown. Do NOT add any overall title or introduction before the 'Childhood' section. Use the following structure EXACTLY:\n\n"
    "Childhood ({child_start}-{child_end})\n"
    "- **Event/Trend Title 1:** [Brief, personalized description of its relevance to a child of that age in {country} (also consider wider UK influences like popular music, TV, or national events where significant) during those years. Maximum 2-3 sentences.]\n"
    "- **Event/Trend Title 2:** [Brief, personalized description as above... Maximum 2-3 sentences.]\n"
    # (Include 3-4 items for this period following the same format)
    "\n"
    "Teenage Years ({teen_start}-{teen_end})\n"
    "- **Event/Trend Title 1:** [Brief, personalized description of its relevance to a teenager of that age in {country} (also consider wider UK influences like popular music, TV, or national events where significant) during those years. Maximum 2-3 sentences.]\n"
    "- **Event/Trend Title 2:** [Brief, personalized description as above... Maximum 2-3 sentences.]\n"
    # (Include 3-4 items for this period following the same format)
    "\n"
    "Young Adult Years ({ya_start}-{ya_end})\n"
    "- **Event/Trend Title 1:** [Brief, personalized description of its relevance to a young adult of that age in {country} (also consider wider UK influences like popular music, TV, or national events where significant) during those years. Maximum 2-3 sentences.]\n"
    "- **Event/Trend Title 2:** [Brief, personalized description as above... Maximum 2-3 sentences.]\n"
    # (Include 3-4 items for this period following the same format)
    "\n"
    "Ensure you provide 3 to 4 bullet-pointed items for each of the three periods.\n"
    "The descriptions for each item MUST be very concise (2-3 sentences maximum) and focus on the personal impact and experience for someone of that specific age primarily in {country}, while acknowledging significant broader UK cultural influences where applicable (e.g., music, national media, major political shifts).\n"
    "The tone should be engaging."
)


def generate_summary(*, child_start: int, child_end: int, teen_start: int, teen_end: int, ya_start: int, ya_end: int, country: str) -> str:
    """Return a cultural-influences summary via LLM.

    If the ``openai`` package or API key is unavailable, a placeholder string
    is returned instead of raising.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if OpenAI is None or not api_key:
        return (
            "(OpenAI API key not configured or library not found, so here is a placeholder.)\n"
            "Imagine descriptions of pop culture, music scenes, and societal "
            "changes spanning the requested years here."
        )

    client = OpenAI(api_key=api_key)
    prompt = _SYSTEM_PROMPT.format(
        child_start=child_start,
        child_end=child_end,
        teen_start=teen_start,
        teen_end=teen_end,
        ya_start=ya_start,
        ya_end=ya_end,
        country=country,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error communicating with OpenAI: {e})"
