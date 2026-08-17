# jinquanhang.com

Personal academic homepage. Hand-written static HTML/CSS — no build system, no
dependencies, no third-party requests. Served by GitHub Pages from this repository.

```
index.html            the whole site
style.css             all styling (light + dark, follows the OS setting)
data/papers.bib       publications — the single source of truth
scripts/build_pubs.py regenerates the publications section from papers.bib
assets/               favicon and the CV (Jinquan-Hang-CV.pdf)
CNAME                 custom domain for GitHub Pages
```

## Adding a publication

1. Add the entry to `data/papers.bib`. Copy the BibTeX from
   [DBLP](https://dblp.org/pid/224/5058), then add the display fields:
   - `venue` — short name shown on the page, e.g. `KDD 2024` (required)
   - `selected` — `yes` to show it on the page (see below)
   - `code` — repository link (optional)
   - `slides` — slides link (optional)
2. Regenerate and publish:

   ```sh
   python3 scripts/build_pubs.py
   git commit -am "Add <paper>" && git push
   ```

The page lists **selected** publications only, but the `.bib` keeps every paper as
the full record. Only entries marked `selected = {yes}` are rendered; the build
prints how many it left out, so a forgotten field is visible rather than silent.
To show everything, mark them all.

Entries are ordered newest year first. Only the region between the `PUBS:START`
and `PUBS:END` markers in `index.html` is rewritten; everything else is hand-edited.
`python3 scripts/build_pubs.py --check` verifies the page matches the `.bib` without
writing anything.

## Editing anything else

Edit `index.html` directly. The page is deliberately short: an identity rail, a
bio, the selected publications, and education. News, projects, and experience
sections existed earlier and are recoverable from git history if ever wanted.

## Preview locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

To check dark mode, switch macOS to Dark Appearance (System Settings → Appearance).

## Still to do

- Add the LinkedIn URL in `index.html` (the link is commented out in the rail).
- The BiLink `[Paper]` link points at a DOI that resolves once the PVLDB issue
  publishes; it 404s until then.

To update the CV, overwrite `assets/Jinquan-Hang-CV.pdf` with a fresh export and
push; the filename stays, so no link changes. The LaTeX source lives outside this
repository. Education stays on the page even with the CV linked: the page serves
readers who skim without downloading anything, which is also why the publications
stay despite appearing in the CV.

## Deployment

Every push to `main` publishes automatically. GitHub Pages serves the repository
as-is; `.nojekyll` disables Jekyll processing.

DNS for the custom domain (records must stay unproxied / DNS-only):

| Type  | Name | Value                                                        |
| ----- | ---- | ------------------------------------------------------------ |
| A     | @    | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| CNAME | www  | jinquanhang.github.io                                        |
