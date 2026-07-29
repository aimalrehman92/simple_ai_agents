"""Tools used by the research agent."""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}
USER_AGENT = "simple-ai-agents/1.0"


def _request_arxiv(params: dict[str, str | int]) -> ET.Element:
    query_string = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{ARXIV_API_URL}?{query_string}",
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content = response.read()
    except Exception as error:
        raise RuntimeError(f"Could not reach the arXiv API: {error}") from error

    try:
        return ET.fromstring(content)
    except ET.ParseError as error:
        raise RuntimeError("arXiv returned an invalid XML response.") from error


def _clean_text(value: str | None) -> str:
    if not value:
        return ""

    return " ".join(value.split())


def _extract_arxiv_id(value: str) -> str:
    value = value.strip()

    patterns = (
        r"arxiv\.org/abs/([^/?#]+)",
        r"arxiv\.org/pdf/([^/?#]+)",
        r"^(?:arXiv:)?\s*([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)$",
        r"^(?:arXiv:)?\s*([a-z-]+(?:\.[A-Z]{2})?/[0-9]{7}(?:v[0-9]+)?)$",
    )

    for pattern in patterns:
        match = re.search(pattern, value, flags=re.IGNORECASE)

        if match:
            arxiv_id = match.group(1)
            if arxiv_id.endswith(".pdf"):
                arxiv_id = arxiv_id[:-4]
            return arxiv_id

    raise ValueError("The input does not contain a valid arXiv identifier.")


def search_arxiv(query: str) -> str:
    """Search arXiv and return a short list of matching papers."""

    query = query.strip()

    if not query:
        raise ValueError("A search query is required.")

    root = _request_arxiv(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 5,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )

    entries = root.findall("atom:entry", ARXIV_NAMESPACE)

    if not entries:
        return f"No arXiv papers were found for '{query}'."

    results: list[str] = []

    for index, entry in enumerate(entries, start=1):
        title = _clean_text(entry.findtext("atom:title", namespaces=ARXIV_NAMESPACE))
        published = _clean_text(
            entry.findtext("atom:published", namespaces=ARXIV_NAMESPACE)
        )
        identifier = _clean_text(
            entry.findtext("atom:id", namespaces=ARXIV_NAMESPACE)
        ).rsplit("/", maxsplit=1)[-1]

        authors = [
            _clean_text(author.findtext("atom:name", namespaces=ARXIV_NAMESPACE))
            for author in entry.findall("atom:author", ARXIV_NAMESPACE)
        ]
        author_text = ", ".join(author for author in authors if author)

        results.append(
            "\n".join(
                [
                    f"{index}. {title}",
                    f"   arXiv ID: {identifier}",
                    f"   Authors: {author_text}",
                    f"   Published: {published[:10]}",
                ]
            )
        )

    return "\n\n".join(results)


def get_paper_details(arxiv_reference: str) -> str:
    """Return metadata for one arXiv paper."""

    arxiv_id = _extract_arxiv_id(arxiv_reference)

    root = _request_arxiv({"id_list": arxiv_id})
    entry = root.find("atom:entry", ARXIV_NAMESPACE)

    if entry is None:
        return f"No paper was found for arXiv ID '{arxiv_id}'."

    title = _clean_text(entry.findtext("atom:title", namespaces=ARXIV_NAMESPACE))
    summary = _clean_text(entry.findtext("atom:summary", namespaces=ARXIV_NAMESPACE))
    published = _clean_text(
        entry.findtext("atom:published", namespaces=ARXIV_NAMESPACE)
    )
    updated = _clean_text(entry.findtext("atom:updated", namespaces=ARXIV_NAMESPACE))

    authors = [
        _clean_text(author.findtext("atom:name", namespaces=ARXIV_NAMESPACE))
        for author in entry.findall("atom:author", ARXIV_NAMESPACE)
    ]

    categories = [
        category.attrib.get("term", "")
        for category in entry.findall("atom:category", ARXIV_NAMESPACE)
    ]

    return "\n".join(
        [
            f"Title: {title}",
            f"arXiv ID: {arxiv_id}",
            f"Authors: {', '.join(author for author in authors if author)}",
            f"Published: {published[:10]}",
            f"Updated: {updated[:10]}",
            f"Categories: {', '.join(category for category in categories if category)}",
            f"Abstract: {summary}",
            f"URL: https://arxiv.org/abs/{arxiv_id}",
        ]
    )


def calculate_paper_age(publication_date: str) -> str:
    """Calculate how long ago a paper was published."""

    publication_date = publication_date.strip()

    if not publication_date:
        raise ValueError("A publication date is required.")

    parsed_date: date | None = None

    for date_format in ("%Y-%m-%d", "%Y"):
        try:
            parsed_date = datetime.strptime(publication_date, date_format).date()
            break
        except ValueError:
            continue

    if parsed_date is None:
        raise ValueError("Use a date in YYYY-MM-DD or YYYY format.")

    today = date.today()

    if parsed_date > today:
        raise ValueError("The publication date cannot be in the future.")

    years = today.year - parsed_date.year
    anniversary_passed = (today.month, today.day) >= (
        parsed_date.month,
        parsed_date.day,
    )

    if not anniversary_passed:
        years -= 1

    days = (today - parsed_date).days

    return (
        f"The paper was published on {parsed_date.isoformat()}. "
        f"It is approximately {years} year(s) old, or {days} days old."
    )