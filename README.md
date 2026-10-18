# 一起找家 / SG Home Finder

Public Singapore rental dashboard. No login or password required.

## Setup

In repository Settings → Pages → Build and deployment, select **GitHub Actions**. No SITE_PASSWORD or external service key is needed. The workflow runs on code pushes, manually, and daily at 08:17 Singapore time (GitHub can delay or disable inactive schedules).

## Data and privacy

`site/data.json` stores the shared snapshot directly in this public repository. Each collection commits its result, retaining Git version history. Source code, criteria, listing links and diagnostics are public. Do not add passwords, personal notes or tenant details. Shared keep/reject/reset decisions are stored in `site/decisions.json`, keyed by source and native listing ID. The crawler never writes this file. Choices are public. Previous device-local favorites are not automatically imported.

## Coverage and current limits

Budget S$2,500; condo within 10 calendar years; Buona Vista, Commonwealth, Queenstown, Redhill, Tiong Bahru; one-north optional. Prioritize private bathrooms; common rooms require subjective review.

RentInSingapore is the active source. On 18 October 2026 the GitHub runner successfully fetched and parsed 20 public listing pages with no source errors. Discovery covers Queenstown, Buona Vista and Tiong Bahru pages, capped at 20 details per run; it is not exhaustive. Cove collection is disabled because its robots.txt disallows detail pages; two historical reference links remain marked stale. Known HDB listings are excluded. Unknown completion years, exact MRT proximity and current availability remain unverified, so a collected room is not automatically a confirmed match.

The crawler respects robots.txt, applies request delays, response limits and timeouts, and pauses a source after access denial/rate limiting. It reads public room facts only, not login-gated contacts. No CAPTCHA, login or access-block bypass is implemented.

## Website isolation

`daily.yml` collects and validates snapshots before committing. `deploy.yml` independently publishes the last committed, validated snapshot on website changes or when collection finishes (including failures). Collection has a 5-minute process deadline and an 8-minute job limit. Writes are atomic; malformed snapshots are rejected. Crawl crashes, missing dependencies, timeouts or push conflicts do not replace the live site. Failed deployments leave the existing Pages deployment intact. Code changes are not automatically retried on conflicting Git pushes. Last successful scrape time and stale flags are shown in the UI.

## Development

Python 3.12+. Install `requirements.txt`, run `python -m unittest discover -s tests -v`, then `python crawler.py`. Preview with `python -m http.server 8000 --directory site`.

`crypto.py` and its regression tests remain for a potential future encrypted mode, but the active crawler and UI do not use them. No encrypted datasets or passwords are published. Tests cover matching, avoiding related-room price contamination, and retaining records after source failure. Browser visual QA has not been performed.

## Shared decisions

The comparison table shows rent, MRT/walk, property type/age, room/bathroom, missing facts, and native source ID. Unknown bathroom details stay unverified.

Click Keep/Reject/Restore, then submit the prefilled GitHub issue. The owner or a repository collaborator must be signed in; add your partner in Settings → Collaborators. Viewing needs no login. Save room decision validates the event, saves the selection, and closes the issue after success. Pages republishes after the workflow; reload choices after deployment. If the issue remains open, inspect Actions. No token is stored in the browser.

The latest submitted issue number wins even if jobs finish out of order. Push conflicts reload and reapply against latest master. Rejected rooms stay hidden in normal views and can be restored in the Rejected tab. Same-source IDs retain decisions across price, URL query and title changes; new listing IDs are treated as new listings. Tests use event fixtures; an authenticated end-to-end decision submission has not been performed.
