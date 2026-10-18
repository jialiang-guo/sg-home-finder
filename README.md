# 一起找家 / SG Home Finder

A password-encrypted Singapore rental dashboard with a daily GitHub Actions crawler.

## Current delivery status

- Implemented: responsive Traditional Chinese UI, password-based decryption, station/room/search filters, sorting, encrypted device-local favorites, incremental crawler, conservative matching, encrypted update diagnostics, and Pages workflow.
- Verified: automated cryptographic and parsing tests; JavaScript syntax. Browser visual QA has not been performed.
- Not deployed: Repository connection is confirmed; Pages and SITE_PASSWORD setup are still required.
- Live source limitation: this development environment receives HTTP 403 from Cove. The adapter is tested against fixtures, NOT a successful live crawl. GitHub's network may also be blocked. This version must not be presented as a working live rental feed until the first real run succeeds and its parsed records are reviewed.
- Source coverage: Cove only. PropertyGuru, 99.co and SRX are not integrated. Cove discovery uses public sitemaps and links, capped at 60 listing pages per run; it is not exhaustive. The source may require an API or adapter changes if its HTML changes.

## User requirements

S$2,500/month; condo age ≤10 calendar years; Buona Vista, Commonwealth, Queenstown, Redhill and Tiong Bahru. one-north is included as optional. Master rooms preferred; common rooms remain review candidates because attractiveness cannot be determined automatically. Dates, lease length, maximum walking distance, and whether bills are included remain unspecified.

Unknown price, building year or availability NEVER counts as a confirmed match. Date-of-completion precision is year-level. Initial HTML adapter deliberately leaves availability unknown unless an adapter enhancement verifies the primary room's availability. Therefore the current source may produce only review candidates. Related-room prices are never treated as the primary room's price. No invented listings or demo results are included in production.

## Deploy on your GitHub

1. Create a repository, preferably private. Push these files, including `.github/workflows/daily.yml`, to its `master` branch. Private-repository GitHub Pages availability depends on your plan. Do not automatically switch the repository to public if unavailable.
2. In **Settings → Secrets and variables → Actions**, add **SITE_PASSWORD**. Use a password manager to generate a unique random password of 24+ characters (code enforces a minimum of 20). Share it privately with your partner. Do not put it in code, issues, workflow inputs, screenshots, or chat.
3. In **Settings → Pages → Build and deployment**, select **GitHub Actions**. This publishes a publicly reachable login shell; rental records are encrypted before publication.
4. Open **Actions → Daily private home search → Run workflow**. The successful deployment step shows the website URL. A final red status can indicate that the site deployed its update warning but crawling failed; inspect the encrypted dashboard diagnostics.
5. Unlock on the website with the password. Confirm source details against the original listings before relying on the feed.

Daily schedule is 00:17 UTC = 08:17 Singapore. GitHub can delay scheduled runs and disable inactive public-repository schedules. Manual runs are always available. No scheduled task is active until the workflow is pushed and enabled.

## Security model and limits

GitHub Pages cannot execute server-side password authentication. This project instead publishes an AES-256-GCM encrypted dataset using a fresh random 16-byte salt and 12-byte nonce per build. Keys use PBKDF2-HMAC-SHA256 with 600,000 iterations; Python and browser use the same AAD/version. The password is a GitHub Actions secret and never goes to the browser as source or a request header. Decryption happens locally via Web Crypto over HTTPS. No plaintext dataset is written by the workflow, committed, cached or uploaded.

The page shell, JavaScript and (if the repo is public) search configuration are public. Encrypted data can be downloaded by anyone and subjected to offline password guessing, hence the strong random-password requirement. This is content encryption, not per-user access control. Someone who knows the password can retain decrypted data; changing a password cannot revoke prior copies. There are no third-party scripts, fonts, analytics, or remote listing-image requests. DOM text uses textContent, not HTML injection.

Favorites are encrypted in localStorage using a domain-separated key and are specific to that browser. Daily listings are shared via the website; favorites and notes are NOT synchronized between partners. Notes are not part of this version. Locking reloads the page and clears in-memory credentials. Changing the shared password makes existing favorites unreadable.

The encrypted prior snapshot is kept in GitHub Actions cache to preserve history and stale records. Caches can be evicted; this is NOT a permanent database or backup. Keep a private backup of `data.enc.json` if permanent history is important. Retrieval errors retain old entries as stale; missing from a crawl does not imply delisting.

## Password rotation

The crawler fails closed if it cannot decrypt the existing state. To preserve history, locally decrypt the backed-up envelope with the old password and re-encrypt with the new password using `crypto.py`, then restore it as `state/data.enc.json` in a trusted run. Do not commit plaintext or either password. For a clean reset, change SITE_PASSWORD, remove existing `homes-*` Actions caches, then run manually. Historical encrypted artifacts may remain decryptable with the old password until retention expires.

## Local development

Python 3.12+ and a current browser with Web Crypto are required.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
# Set SITE_PASSWORD using your shell's hidden-input or secret-manager mechanism.
python crawler.py
python -m http.server 8000 --directory site
```

Visit http://localhost:8000 (localhost is a secure context for Web Crypto). Do not commit the generated `site/data.enc.json` or `state/` files. Edit `config.json` for stations, budget and crawl caps. Python collector waits at least 3 seconds between requests, honors robots.txt, limits responses and only accesses HTTPS cove.sg URLs. It fails closed for missing robots access, redirects, access blocks or parse failures. It does not bypass CAPTCHA, logins or restrictions. A blocked adapter needs source/API review before being enabled.

## Files

- `crawler.py`: discovery, parsing, conservative classification, snapshot merge and encryption.
- `crypto.py`: shared envelope format.
- `site/`: static private-data dashboard.
- `tests/`: privacy, matching and parsing checks.
- `.github/workflows/daily.yml`: scheduled collection and Pages deployment.
