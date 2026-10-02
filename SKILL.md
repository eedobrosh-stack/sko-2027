---
name: sko_2027
description: Ski-trip apartment finder. Reads spec.json (dates, group, beds, resorts, budget, quality bar, email settings), scans ski resorts and listing sites (Airbnb, Booking.com, Vrbo, agencies) for apartments that fit, writes a ranked candidates list for approval, then creates reservation-inquiry email DRAFTS (never sends) in the user's Gmail. Use for "/sko_2027 run", "/sko_2027 drafts", "/sko_2027 spec", "find a ski apartment", "chalet search".
---

# sko_2027: ski apartment finder

Commands (args after the skill name):
- `run`: scan, filter, rank, write results. Reads `spec.json`.
- `drafts`: create Gmail drafts for candidates with `approved: true`.
- `spec`: start `python3 server.py` from this folder and tell the user to open http://localhost:7894 to edit the spec.
- no args: if `spec.json` is missing, do `spec`; otherwise summarise the spec and ask whether to `run`.

The spec is the single source of truth. Never hardcode trip details. Folder: this skill's directory (contains `spec.json`, `server.py`, `form/`, `references/`). Output folder: `output_dir` from the spec (expand `~`), files: `candidates.json`, `drafts.json`, `scans/*.md`.

## `run`

1. **Read and restate the spec** in two lines (dates, nights, group, beds, budget, drive limit). Compute nights from the dates. If a required field is empty (dates, airport, adults, budget, gmail), stop and ask the user to fill the form.
2. **Plan regions.** List ski resorts within `max_drive_hours` of the airport, grouped into 3 to 5 regional clusters (use real drive-time knowledge, then verify with rome2rio or OSRM). Always include `preferred_resorts` even if over the limit, and flag them "over limit". Never silently drop a preferred resort.
3. **Fetch pass (parallel agents, one per cluster).** Each agent uses WebSearch and WebFetch only, applies the hard rules below, and returns 5 to 10 candidates plus near-misses with reasons. Save each report to `<output_dir>/scans/<cluster>.md`.
4. **Chrome pass (premium and gap filling).** Booking, Vrbo, Interhome and Airbnb block fetch-based agents, so run them in the user's Chrome with the Claude in Chrome tools. Follow `references/chrome_recipes.md` exactly (URL templates, JS extractors, batching limits). Cover the price band from `ideal_total` to a bit above `max_total`, not just cheap listings, and page through more than the first page.
5. **Filter with hard rules** (from the spec):
   - drive from the airport within the limit (or flagged),
   - real beds >= `real_beds_required`; sofa beds do not count unless `allow_sofa_beds`; prefer single beds,
   - lift within walking distance; if `driving_to_lifts_is_showstopper`, drop anything needing a car, shuttle or bus to reach lifts,
   - every `must_haves` item present; none of `deal_breakers`,
   - quality at the stated tier (reviews, finish, renovation year, photos),
   - total for the exact dates within `max_total` (flag up to about 10 percent over as "over budget, exceptional" only).
6. **Verify, do not assume.** For each finalist open the listing with the exact dates and 6 adults and read: total price, bed configuration per bedroom, distance to the nearest lift, availability. Mark prices "confirmed for dates" or "est." For every aggregator hit also search Google for the owner or direct site and an email address (only record emails seen on a page, never guess).
7. **Write `candidates.json`** (array). Fields per item: `n` (1..N, or "P1".. for premium), `name`, `resort`, `drive`, `url`, `contact` (platform or phone), `email` (or null), `price`, `beds`, `lift`, `notes`, `tier` ("shortlist" or "premium"), `approved: null`. Keep an existing file's `approved` flags when re-running (match by url).
8. Tell the user to open the form's Results tab (http://localhost:7894, start with `python3 server.py`) or read `candidates.json`, tick Approve, then run `/sko_2027 drafts`. Give a short summary: how many candidates, price range, best 3, and honest coverage gaps (what was blocked or not searched).

Be honest about coverage. If a pass found little, say what it did not cover instead of implying the market is exhausted.

## `drafts`

Read `candidates.json` where `approved` is true and `spec.email`. For each, write a short email per `references/email_template.md` (language and signer from the spec, subject from `subject_template` with `{name}` and `{dates}`), then create it as a Gmail DRAFT in `email.gmail_account` through Chrome. Never click Send. Follow the Gmail section of `references/chrome_recipes.md`. Put `email` in To when known; for platform-only listings leave To empty and tell the user to paste the body into the platform's message box. Save bodies to `<output_dir>/drafts.json`. Finish by listing which drafts have a recipient and which need the platform.

## Rules

- Draft only, never send, never submit forms on listing sites, never pay, never create accounts.
- Do not enter passwords. If a site needs login, ask the user to sign in in Chrome.
- Keep each browser batch small (3 to 5 navigations). Long batches time out.
- Prices and availability change; state the date they were read.
