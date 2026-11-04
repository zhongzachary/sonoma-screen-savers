# Wallpaper website

The website is a static page with no build step or third-party dependencies. It reads `data/entries.json` and the individual `data/locales/<locale>.json` files directly, using each file's `localizedStrings` object for translations. Preview filenames in `preview_images/` use uppercase asset IDs; the site and README generator both use those paths.

## Preview locally

Run this command from the repository root:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000/`. Use an HTTP server rather than opening `index.html` directly, because the page fetches the JSON files.

## Languages

- A URL without `lang` always displays English, regardless of browser language or past selections.
- Use `?lang=ja` or `?lang=zh-TW` to link to a language. Locale matching ignores case and accepts either hyphens or underscores.
- An unsupported language falls back to English. Missing individual translations and unavailable locale files also fall back to English.
- English loads initially for fallback; other locale files load only when requested and are cached for the current page session. Rapid language changes and browser navigation cannot let an older request overwrite the latest selection.
- Selecting a language updates the URL without reloading. Browser Back and Forward restore the language from the URL. No cookies or local storage are used.
- Only category names, wallpaper captions, and matching category-navigation labels translate. Other interface text remains English. The `portrait` and `landscape` suffixes stay English and use a smaller, lighter font.
- Supported locale identifiers and their native language-picker labels live in `site.js`. When adding a locale file, add a matching entry there. Locale identifiers use hyphens, matching the filenames in `data/locales/`.

## Layout and media

The gallery includes every asset in one continuous grid per category, without subcategory headings. Assets remain ordered by category, subcategory, and asset `preferredOrder`. Previews retain their original proportions and wrap across two columns below 640 pixels, three columns from 640 pixels, and four columns from 900 pixels. Captions are not links; only preview images open videos in a new tab. Videos remain on Apple's servers and are never embedded or downloaded by the page.

Colors follow the visitor's system light/dark preference. The title, typography, heading rules, and spacing are intentionally similar to rendered GitHub Markdown.

## Hosting

The repository root contains `index.html`, so it can be hosted directly as a static GitHub Pages site without a build command. Keep `site.css`, `site.js`, `data/`, and `preview_images/` alongside it. All gallery paths are relative, including when hosted under `/sonoma-screen-savers/`.

Publishing the site is a separate step: the local implementation does not change GitHub Pages settings or push commits.
