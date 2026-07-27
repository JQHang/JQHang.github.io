# jinquanhang.com

Personal academic homepage. Hand-written static HTML/CSS — no build system, no
dependencies, no third-party requests. Served by GitHub Pages from this repository.

```
index.html            the whole site
style.css             all styling (light + dark, follows the OS setting)
data/papers.bib       publications — the single source of truth
scripts/build_pubs.py regenerates the publications section from papers.bib
assets/               portrait and favicon
CNAME                 custom domain for GitHub Pages
```

## Adding a publication

1. Add the entry to `data/papers.bib`. Copy the BibTeX from
   [DBLP](https://dblp.org/pid/224/5058), then add the display fields:
   - `venue` — short name shown on the page, e.g. `KDD 2024` (required)
   - `code` — repository link (optional)
   - `slides` — slides link (optional)
2. Regenerate and publish:

   ```sh
   python3 scripts/build_pubs.py
   git commit -am "Add <paper>" && git push
   ```

Entries are ordered newest year first. Only the region between the `PUBS:START`
and `PUBS:END` markers in `index.html` is rewritten; everything else is hand-edited.
`python3 scripts/build_pubs.py --check` verifies the page matches the `.bib` without
writing anything.

## Editing anything else

Edit `index.html` directly — news, projects, experience, and education are plain
HTML in document order.

## Preview locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

To check dark mode, switch macOS to Dark Appearance (System Settings → Appearance).

## Still to do

- Replace `assets/photo.svg` with a real headshot. Save it as `assets/photo.jpg`
  and update the `src` on the `<img class="portrait">` tag in `index.html`.
- Add an English CV as `assets/cv.pdf`, then uncomment the CV link in `index.html`.
- Add the LinkedIn URL in `index.html` (the link is commented out next to the CV one).
- Link JoinMiner once joinminer.com is live (a commented-out line in the Projects
  section shows exactly what to uncomment).

## Deployment

Every push to `main` publishes automatically. GitHub Pages serves the repository
as-is; `.nojekyll` disables Jekyll processing.

DNS for the custom domain (records must stay unproxied / DNS-only):

| Type  | Name | Value                                                        |
| ----- | ---- | ------------------------------------------------------------ |
| A     | @    | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| CNAME | www  | jqhang.github.io                                             |
