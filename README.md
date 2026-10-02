# sko_2027: ski apartment finder for Claude Code

Tell it your dates, group, beds, budget and standards once. Claude scans ski resorts and listing sites, builds a ranked list, you tick the ones you like, and it creates inquiry-email **drafts** in your Gmail. It never sends anything.

## You need
- [Claude Code](https://claude.com/claude-code)
- The Claude in Chrome extension, with Chrome signed in to Gmail (and ideally Airbnb)
- Python 3 (standard library only) for the optional local form server

## Install
```bash
git clone https://github.com/eedobrosh-stack/sko-2027 ~/.claude/skills/sko_2027
cd ~/.claude/skills/sko_2027 && cp spec.example.json spec.json
```
(or clone anywhere and run `./install.sh`).

## Use
1. Start the form: `python3 ~/.claude/skills/sko_2027/server.py` and open http://localhost:7894
2. Fill in the **Trip spec** tab: dates, airport, group, beds, resorts, budget, quality bar, your Gmail address, your name, and the output folder (a Google Drive folder path works). Click **Save**.
3. Click **Save & run in Claude (Terminal)** (macOS), or **Copy run command** and paste `claude "/sko_2027 run"` into any terminal.
4. When it finishes, open the **Results & approvals** tab, tick the apartments you like, **Save approvals**.
5. Click **Save & create email drafts in Claude**, or run `claude "/sko_2027 drafts"`. Drafts appear in your Gmail Drafts folder. Open each, check it, send it yourself. Listings that only exist on Airbnb or Booking have no public email: paste the draft body into the platform's message box.

Without the server you can open `form/index.html` directly: use **Download spec.json** and drop the file in the skill folder.

## What it does
- Plans resorts within your drive limit of the airport (and always includes the ones you named).
- Runs parallel research agents for the web pass, then a Chrome pass on Booking, Airbnb and Vrbo with your exact dates (those sites block plain fetching).
- Applies your hard rules: real beds (sofa beds do not count by default), walkable to a lift, kitchen, budget for the exact dates, quality tier.
- Verifies finalists on the listing page (price, beds per bedroom, lift distance, availability) and looks for owner emails.

## Files
| File | Purpose |
| --- | --- |
| `SKILL.md` | The skill instructions Claude follows |
| `spec.example.json` | Starting spec (your own `spec.json` is git-ignored) |
| `form/index.html`, `server.py` | Local spec form, results page, launch button |
| `references/chrome_recipes.md` | Tested Booking/Airbnb/Gmail browser recipes and pitfalls |
| `references/email_template.md` | Inquiry email structure |

## Notes
- Prices and availability are read at run time; re-check before booking.
- Search coverage is limited by what the sites show to an automated browser. The skill reports what it could not cover.
- Everything stays on your machine. The skill never sends email, pays, or creates accounts.
