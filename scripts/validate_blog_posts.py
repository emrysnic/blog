#!/usr/bin/env python3
"""Validate that blog post dates, archive entries, and homepage links stay aligned.

This catches the class of mistakes where a post folder, its visible date, or the
home/archive references drift apart.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
POST_DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
META_DATE_RE = re.compile(r'class="meta">(\d{4}-\d{2}-\d{2})\b')
ARCHIVE_ITEM_RE = re.compile(
    r'<a href="(?P<href>\d{4}-\d{2}-\d{2}[^/]+/)">(?P<title>[^<]+)</a>\s*—\s*(?P<date>\d{4}-\d{2}-\d{2})'
)
HOME_CARD_RE = re.compile(r'<article class="post-card[^>]*>(?P<body>.*?)</article>', re.S)
HOME_CARD_HREF_RE = re.compile(r'href="posts/(?P<href>\d{4}-\d{2}-\d{2}[^/]+/)"')
HOME_CARD_DATE_RE = re.compile(r'<p class="post-meta">(?P<date>\d{4}-\d{2}-\d{2})\s*·')


def error(messages: list[str], message: str) -> None:
    messages.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    if not POSTS_DIR.exists():
        error(errors, f"missing posts directory: {POSTS_DIR}")
        print("\n".join(errors), file=sys.stderr)
        return 1

    posts = []
    for post_dir in sorted(p for p in POSTS_DIR.iterdir() if p.is_dir()):
        match = POST_DIR_RE.match(post_dir.name)
        if not match:
            error(errors, f"post directory name does not start with YYYY-MM-DD: {post_dir.relative_to(ROOT)}")
            continue

        folder_date = match.group(1)
        post_file = post_dir / "index.html"
        if not post_file.exists():
            error(errors, f"missing post file: {post_file.relative_to(ROOT)}")
            continue

        html = read_text(post_file)
        meta = META_DATE_RE.search(html)
        if not meta:
            error(errors, f"missing meta date in {post_file.relative_to(ROOT)}")
            continue

        meta_date = meta.group(1)
        if meta_date != folder_date:
            error(
                errors,
                f"date mismatch in {post_file.relative_to(ROOT)}: folder={folder_date} meta={meta_date}",
            )

        posts.append(
            {
                "dir": post_dir.name,
                "date": folder_date,
            }
        )

    if not posts:
        error(errors, "no posts found")
        print("\n".join(errors), file=sys.stderr)
        return 1

    posts_sorted = sorted(posts, key=lambda item: item["dir"])
    latest = posts_sorted[-1]["dir"]

    home_html = read_text(ROOT / "index.html")
    archive_html = read_text(ROOT / "posts" / "index.html")

    home_cards = []
    for match in HOME_CARD_RE.finditer(home_html):
        body = match.group("body")
        href_match = HOME_CARD_HREF_RE.search(body)
        date_match = HOME_CARD_DATE_RE.search(body)
        if href_match and date_match:
            home_cards.append({"href": href_match.group("href"), "date": date_match.group("date")})

    home_card_hrefs = [f"posts/{item['href']}" for item in home_cards]
    home_card_dates = [item["date"] for item in home_cards]
    expected_home_hrefs = [f"posts/{post['dir']}/" for post in posts_sorted[::-1]]
    expected_home_dates = [post["date"] for post in posts_sorted[::-1]]

    if home_card_hrefs != expected_home_hrefs:
        error(
            errors,
            "homepage card links are wrong: expected "
            + ", ".join(expected_home_hrefs)
            + " but saw "
            + ", ".join(home_card_hrefs),
        )

    if home_card_dates != expected_home_dates:
        error(
            errors,
            "homepage card dates are wrong: expected "
            + ", ".join(expected_home_dates)
            + " but saw "
            + ", ".join(home_card_dates),
        )

    archive_links = [m.groupdict() for m in ARCHIVE_ITEM_RE.finditer(archive_html)]
    archive_hrefs = [item["href"] for item in archive_links]
    archive_dates = [item["date"] for item in archive_links]
    expected_hrefs = [f"{post['dir']}/" for post in posts_sorted[::-1]]
    expected_dates = [post["date"] for post in posts_sorted[::-1]]

    if archive_hrefs != expected_hrefs:
        error(
            errors,
            "archive order or links are wrong: expected "
            + ", ".join(expected_hrefs)
            + " but saw "
            + ", ".join(archive_hrefs),
        )

    if archive_dates != expected_dates:
        error(
            errors,
            "archive dates are wrong: expected "
            + ", ".join(expected_dates)
            + " but saw "
            + ", ".join(archive_dates),
        )

    for post in posts_sorted:
        href = f"posts/{post['dir']}/"
        if href not in home_html:
            error(errors, f"homepage missing post link: {href}")
        if f'{post["dir"]}/' not in archive_html:
            error(errors, f"archive missing post link: {post['dir']}/")

    if errors:
        print("Blog validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print(f"OK: {len(posts_sorted)} post(s) validated; latest is {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
