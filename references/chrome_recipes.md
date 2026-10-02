# Chrome recipes (Claude in Chrome tools)

Load the tools first: ToolSearch `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_close_mcp`. Call `tabs_context_mcp {createIfEmpty:true}` first, work in one tab, close it at the end.

General: `browser_batch` runs actions sequentially; keep batches to 3 to 5 navigations or the call times out. Use `javascript_tool` to extract data instead of screenshots. Wait 4 to 6 s after navigating.

## Booking.com search (reliable)

URL (adjust ss, dates, adults, bedroom count):
`https://www.booking.com/searchresults.en-gb.html?ss=<Resort>&checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&group_adults=6&no_rooms=1&group_children=0&selected_currency=EUR&nflt=ht_id%3D201%3Bht_id%3D220%3Bht_id%3D213%3Bentire_place_bedroom_count%3D3%3Bprice%3DEUR-<min>-<max>-1&order=price_desc`
(ht_id 201 apartments, 220 holiday homes, 213 villas.) The price filter is a TOTAL for the stay, but Booking silently ignores it for some resorts and sometimes returns one empty card; if so, drop the filter and filter the results yourself.

Extractor (returns total price for the stay, bed configuration, distance, rating):
```js
await new Promise(r=>setTimeout(r,4000));
[...document.querySelectorAll('[data-testid="property-card"]')].slice(0,25).map(c=>({
 t:c.querySelector('[data-testid="title"]')?.innerText,
 p:c.querySelector('[data-testid="price-and-discounted-price"]')?.innerText,
 d:c.querySelector('[data-testid="distance"]')?.innerText,
 rv:c.querySelector('[data-testid="review-score"]')?.innerText?.replace(/\n/g,' '),
 cfg:c.querySelector('[data-testid="recommended-units"]')?.innerText?.replace(/\n/g,' | ').slice(0,230),
 l:c.querySelector('a[data-testid="title-link"]')?.href?.split('?')[0]}))
```
"d" is distance from the town centre, not from the lifts. On a property page (add the dates to the URL) read the "Ski lifts" block: `t.indexOf('Ski lifts')` in `document.body.innerText`, and the bed lines. Booking's `cfg` lists beds as "singles / large doubles / sofa beds"; a double means two people share.

## Airbnb search

`https://www.airbnb.com/s/<Resort>--<Country>/homes?checkin=...&checkout=...&adults=6&min_bedrooms=3&min_beds=6&price_min=<per night>&price_max=<per night>&room_types%5B%5D=Entire%20home%2Fapt&currency=EUR`
Airbnb's price filters are PER NIGHT. Cards: `[data-testid="card-container"]`; use `.innerText` (contains bedrooms, beds, baths, "€X total", rating) and `a.href`. Cards labelled "Feb 16 to 20" are alternative dates (not available for yours). Open listings with `?check_in=...&check_out=...&adults=6&currency=EUR` and read: `h1`, "N guests, N bedrooms, N beds", the "Where you'll sleep" block (`indexOf('Where you')`), sentences mentioning lift, gondola, slope, walking, ski-in; text "not available" means the dates are booked. Airbnb never exposes host emails.

## Vrbo
`https://www.vrbo.com/search?destination=<Resort>%2C%20<Country>&startDate=...&endDate=...&adults=6&sort=PRICE_HIGH_TO_LOW&bedrooms=3&currency=EUR` renders cards but is often rate limited.

## Finding owner emails
Search the property name plus address, and the licence/CIN code shown on the listing. Official sites often hide emails behind scripts: read the raw HTML footer or `mailto:` links. Only record emails you saw on a page. Many Booking-only private hosts have no public email; say so.

## Gmail drafts (personal account)

The Claude.ai Gmail connector often lacks compose scope, so create drafts in Chrome at mail.google.com. Find the account index: navigate to `https://mail.google.com/mail/u/?authuser=<gmail_account>`; the URL then shows `/mail/u/<n>/`. Use that `<n>`.

Working recipe per draft (verified on 20 drafts):
1. Click the Compose button (top left, about x150 y96) to open a NEW compose window.
2. JavaScript: assert there is exactly one empty `input[name="subjectbox"]` and one empty `div[aria-label="Message Body"]`, otherwise stop. Then fill with `document.execCommand('insertText', false, text)`: first the To input `input[aria-label="To recipients"]` (focus it first; skip if no email), then the subject input, then the body (focus the div, `getSelection().selectAllChildren(body); collapseToStart()` then insertText; use "\n" for line breaks).
3. JavaScript: click `[aria-label="Save & close"]` and wait 2.5 s. This saves the draft.
4. Verify with the sidebar label "Drafts N" (count goes up by one).

Do NOT: type the body with keystrokes (Gmail shortcuts like "?" eat it), use `?view=cm&body=` compose URLs (they never save), or navigate to `#inbox?compose=new` repeatedly (it reuses the open window and appends text into it). To add a recipient to an existing draft: search `in:drafts subject:"..."`, open the row (use `find` to get its ref, then click the ref), insertText into the To input, then Save & close.

## Google Maps (find owners' own websites)

`https://www.google.com/maps/search/luxury+apartments+chalet+rental+<Resort>` works in Chrome without a login. Scroll `div[role="feed"]` 3 to 4 times, then:
```js
const f=document.querySelector('div[role="feed"]');for(let i=0;i<3;i++){f.scrollTo(0,f.scrollHeight);await new Promise(r=>setTimeout(r,1400));}
[...document.querySelectorAll('div[role="feed"] > div')].filter(d=>d.querySelector('a.hfpxzc')).map(d=>({
 n:d.querySelector('a.hfpxzc')?.getAttribute('aria-label'),
 r:(d.querySelector('span.MW4etd')?.innerText||'')+(d.querySelector('span.UY7F9')?.innerText||''),
 c:(d.innerText.split('\n')[3]||'').slice(0,40),
 w:[...d.querySelectorAll('a')].find(a=>a.getAttribute('data-value')==='Website')?.href}))
```
About 15 to 18 cards load per search. Drop hotels, shops, and URLs on booking.com, airbnb, freecancellations, bluepillow, facebook. Cards with no Website button usually only exist on platforms. Google web search (google.com/search?q=...) also works in Chrome for finding an owner site; drop booking-site mirrors by domain.
