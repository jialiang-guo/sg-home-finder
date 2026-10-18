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

## Shared decisions (Supabase)

Choices now live in Supabase home_decisions, using the original source listing keys. The crawler never changes that table. site/decisions.json is a historical snapshot; the old issue writer is disabled to avoid two conflicting stores. At migration it contained no selections.

The frontend uses vendored @supabase/supabase-js 2.118.0 and only a publishable key. Supabase Auth email/password sessions persist on the user's device; passwords are never committed. Public reads preserve the existing public dashboard behavior. Writes require an authenticated UUID in home_members. The allowlist has RLS and no client write grants. No service-role key is present in the website.

Run supabase/schema.sql once for initial setup. In Authentication → Users → Add user → Create new user, create each selection account yourself with a password and confirmed email. Never put passwords in SQL or repository files. Add each intended account UUID to home_members using the SQL editor (do not automatically authorize everyone in auth.users). Log in on the website using this selection account, not the Supabase dashboard/GitHub password.

Changes save before the UI acknowledges success. Failed saves retain the original choice. Other devices refresh every 30 seconds while visible and on focus. Rejected records persist and are reversible. Reset stores an explicit reset row. Same-source IDs retain decisions across daily collection; new source IDs are new listings. Free Supabase projects may pause after inactivity. If the database is unavailable, writes stop; the website does not overwrite choices from its old GitHub snapshot.

Validation: Python regression suite, JavaScript syntax and store tests, and SQL checks for anonymous/non-member write denial. Creating the two login accounts and authenticated UI save verification require the account owner's input.
