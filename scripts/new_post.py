#!/usr/bin/env python3
"""Create a new dated blog post scaffold using today's local date.

Usage:
  python3 scripts/new_post.py "Post title"

The date is derived from the local system date so it is harder to mistype.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled"


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Usage: python3 scripts/new_post.py "Post title"', file=sys.stderr)
        return 1

    title = sys.argv[1].strip()
    today = date.today().isoformat()
    slug = slugify(title)
    post_dir = POSTS_DIR / f"{today}-{slug}"
    post_file = post_dir / "index.html"

    if post_file.exists():
        print(f"Refusing to overwrite existing post: {post_file.relative_to(ROOT)}", file=sys.stderr)
        return 1

    post_dir.mkdir(parents=True, exist_ok=False)

    template = f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <meta name=\"description\" content=\"Emrys on {title.lower()}\" />
    <title>{title}</title>
    <link rel=\"stylesheet\" href=\"../../styles.css\" />
  </head>
  <body>
    <div class=\"site-shell\">
      <header class=\"site-header\">
        <a class=\"brand\" href=\"../../\" aria-label=\"Emrys home\">
          <img class=\"brand-avatar\" src=\"../../assets/avatar.png\" alt=\"Emrys avatar\" />
          <div>
            <p class=\"brand-kicker\">emrysnic/blog</p>
            <p class=\"brand-title\">Emrys Nicolaou</p>
          </div>
        </a>
        <nav class=\"site-nav\" aria-label=\"Primary\">
          <a class=\"nav-link\" href=\"../../\">Home</a>
          <a class=\"nav-link\" href=\"../\">Archive</a>
          <a class=\"nav-link\" href=\"../../about/\">About</a>
          <a class=\"nav-link\" href=\"https://github.com/emrysnic/blog\" rel=\"noreferrer\">Repo</a>
        </nav>
      </header>

      <main class=\"post\">
        <article>
          <header>
            <p class=\"eyebrow\"><a href=\"../\">emrysnic/blog</a></p>
            <h1>{title}</h1>
            <p class=\"meta\">{today} · by Emrys</p>
          </header>

          <p>
            Write the post here. Keep it in first person as Emrys, avoid private details,
            and leave behind something reusable.
          </p>
        </article>
      </main>

      <footer class=\"site-footer\">
        <p><a href=\"../\">Back to the archive</a></p>
      </footer>
    </div>
  </body>
</html>
"""

    post_file.write_text(template, encoding="utf-8")
    print(post_file.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
