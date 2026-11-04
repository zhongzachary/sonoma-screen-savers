# Wallpaper website

The website is a static page with no build step or third-party dependencies. It reads `data/entries.json` and `data/localizations.json` directly and displays the existing files in `preview_images/`. Refreshing those files updates both the gallery content and the available languages; there is no separate wallpaper catalogue to maintain.

## Preview locally

Run this command from the repository root:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000/`. Use an HTTP server rather than opening `index.html` directly, because the page fetches the JSON files.

## Languages

- A URL without `lang` always displays English, regardless of browser language or past selections.
- Use `?lang=ja` or `?lang=zh-TW` to link to a language. Locale matching ignores case and accepts either hyphens or underscores.
- An unsupported language falls back to English. Missing individual translations also fall back to the English string.
- Selecting a language updates the URL without reloading. Browser Back and Forward restore the language from the URL. No cookies or local storage are used.
- Only categories, subcategories, wallpaper captions, and matching category-navigation labels translate. Other interface text remains English. The `portrait` and `landscape` suffixes stay English and use a smaller, lighter font.
- Native language-picker labels live in `site.js`. Add a label there if adding a new locale; an unlisted locale still appears using its identifier.

## Layout and media

The gallery includes every asset, ordered by category, subcategory, and asset `preferredOrder`. Previews retain their original proportions and wrap across two columns below 640 pixels, three columns from 640 pixels, and four columns from 900 pixels. Captions are not links; only preview images open videos in a new tab. Videos remain on Apple's servers and are never embedded or downloaded by the page.

Colors follow the visitor's system light/dark preference. The title, typography, heading rules, and spacing are intentionally similar to rendered GitHub Markdown.

## Hosting

The repository root contains `index.html`, so it can be hosted directly as a static GitHub Pages site without a build command. Keep `site.css`, `site.js`, `data/`, and `preview_images/` alongside it. All gallery paths are relative, including when hosted under `/sonoma-screen-savers/`.

Publishing the site is a separate step: the local implementation does not change GitHub Pages settings or push commits.
