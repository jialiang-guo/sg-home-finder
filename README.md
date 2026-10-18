# 一起找家 / SG Home Finder

Public Singapore rental dashboard. No login or password required.

## Setup

In repository Settings → Pages → Build and deployment, select **GitHub Actions**. No SITE_PASSWORD or external service key is needed. The workflow runs on code pushes, manually, and daily at 08:17 Singapore time (GitHub can delay or disable inactive schedules).

## Data and privacy

`site/data.json` stores the shared snapshot directly in this public repository. Each collection commits its result, retaining Git version history. Source code, criteria, listing links and diagnostics are public. Do not add passwords, personal notes or tenant details. Favorites remain device-local in localStorage, not synced to GitHub. Shared favorites/notes would need authenticated write access and are not implemented.

## Coverage and current limits

Budget S$2,500; condo within 10 calendar years; Buona Vista, Commonwealth, Queenstown, Redhill, Tiong Bahru; one-north optional. Prioritize private bathrooms; common rooms require subjective review.

Cove is the only implemented source. Initial records are two real reference links previously reviewed, NOT confirmed available or within-budget listings. Their current prices, completion years and availability are unknown. The development environment returned 403; successful live crawling is not yet verified. Sitemap discovery is limited to 60 listing pages and is not exhaustive. Related-room prices are excluded. All unverified facts stay unknown; failures retain previous records as stale and are shown in the dashboard. A successful deployment does not prove a successful crawl.

The crawler respects robots.txt, rate limits requests and does not bypass access blocks. If GitHub runners are also blocked, a different supported source or API is needed. The adapter conservatively leaves availability unknown, so candidates require confirmation on the original site.

## Development

Python 3.12+. Install `requirements.txt`, run `python -m unittest discover -s tests -v`, then `python crawler.py`. Preview with `python -m http.server 8000 --directory site`.

`crypto.py` and its regression tests remain for a potential future encrypted mode, but the active crawler and UI do not use them. No encrypted datasets or passwords are published. Tests cover matching, avoiding related-room price contamination, and retaining records after source failure. Browser visual QA has not been performed.
