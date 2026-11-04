const languageNames = {
  ar: "العربية",
  ca: "Català",
  cs: "Čeština",
  da: "Dansk",
  de: "Deutsch",
  el: "Ελληνικά",
  en: "English",
  "en-AU": "English (Australia)",
  "en-CA": "English (Canada)",
  "en-GB": "English (United Kingdom)",
  "en-IN": "English (India)",
  "en-PH": "English (Philippines)",
  es: "Español",
  "es-419": "Español (Latinoamérica)",
  "es-US": "Español (Estados Unidos)",
  fi: "Suomi",
  fr: "Français",
  "fr-CA": "Français (Canada)",
  he: "עברית",
  hi: "हिन्दी",
  hr: "Hrvatski",
  hu: "Magyar",
  id: "Bahasa Indonesia",
  it: "Italiano",
  ja: "日本語",
  ko: "한국어",
  ms: "Bahasa Melayu",
  nl: "Nederlands",
  no: "Norsk",
  pl: "Polski",
  "pt-BR": "Português (Brasil)",
  "pt-PT": "Português (Portugal)",
  ro: "Română",
  ru: "Русский",
  sk: "Slovenčina",
  sl: "Slovenščina",
  sv: "Svenska",
  th: "ไทย",
  tr: "Türkçe",
  uk: "Українська",
  vi: "Tiếng Việt",
  "zh-CN": "简体中文（中国大陆）",
  "zh-HK": "繁體中文（香港）",
  "zh-TW": "繁體中文（台灣）",
};

const languagePicker = document.getElementById("language");
const categoryList = document.getElementById("categories");
const gallery = document.getElementById("gallery");
const status = document.getElementById("status");

function normalizeLanguage(language) {
  return language.replaceAll("_", "-").toLowerCase();
}

function byPreferredOrder(first, second) {
  return (first.preferredOrder ?? 0) - (second.preferredOrder ?? 0);
}

async function readJSON(filename) {
  const response = await fetch(filename);
  if (!response.ok) {
    throw new Error(`Unable to load ${filename}: ${response.status}`);
  }
  return response.json();
}

function createWallpaper(asset, translate, language) {
  const name = translate(asset.localizedNameKey);
  const orientation = asset.variant?.orientation;
  const figure = document.createElement("figure");
  const preview = document.createElement("a");
  preview.className = "preview";
  preview.href = asset["url-4K-SDR-240FPS"];
  preview.target = "_blank";
  preview.rel = "noopener noreferrer";

  const image = document.createElement("img");
  image.src = `./preview_images/${asset.id.toUpperCase()}.png`;
  image.alt = "";
  image.loading = "lazy";
  image.decoding = "async";
  preview.append(image);

  const caption = document.createElement("figcaption");
  const captionId = `caption-${asset.id}`;
  caption.id = captionId;
  const captionName = document.createElement("bdi");
  captionName.textContent = name;
  caption.append(captionName);

  if (orientation) {
    const variant = document.createElement("span");
    variant.className = "orientation";
    variant.lang = "en";
    variant.dir = "ltr";
    variant.textContent = orientation;
    caption.append(" ", variant);
  }

  const linkHint = document.createElement("span");
  linkHint.id = `video-hint-${asset.id}`;
  linkHint.hidden = true;
  linkHint.lang = "en";
  linkHint.textContent = "Open full video in a new tab";
  preview.setAttribute("aria-labelledby", captionId);
  preview.setAttribute("aria-describedby", linkHint.id);
  figure.lang = language;
  figure.append(preview, caption, linkHint);
  return figure;
}

async function main() {
  try {
    const [entries, english] = await Promise.all([
      readJSON("./data/entries.json"),
      readJSON("./data/locales/en.json"),
    ]);
    const englishNames = new Map(Object.entries(english.localizedStrings));
    const translations = new Map([["en", Promise.resolve(englishNames)]]);
    const languages = new Map(Object.keys(languageNames).map((language) => [
      normalizeLanguage(language), language,
    ]));
    const categories = [...entries.categories].sort(byPreferredOrder);
    const assets = [...entries.assets].sort(byPreferredOrder);
    let renderVersion = 0;

    function loadTranslations(language) {
      if (!translations.has(language)) {
        const pending = readJSON(`./data/locales/${language}.json`)
          .then(({ localizedStrings }) => new Map(Object.entries(localizedStrings)));
        translations.set(language, pending);
        pending.catch(() => translations.delete(language));
      }
      return translations.get(language);
    }

    const options = Object.keys(languageNames)
      .sort((first, second) => {
        if (first === "en") return -1;
        if (second === "en") return 1;
        return first.localeCompare(second, "en");
      })
      .map((language) => {
        const option = document.createElement("option");
        option.value = language;
        option.lang = language.replaceAll("_", "-");
        option.textContent = languageNames[language] ?? language;
        return option;
      });
    languagePicker.replaceChildren(...options);

    async function render() {
      const version = ++renderVersion;
      const requested = new URL(window.location.href).searchParams.get("lang") ?? "en";
      let language = languages.get(normalizeLanguage(requested)) ?? "en";
      let localizedNames;
      status.hidden = false;
      try {
        localizedNames = await loadTranslations(language);
      } catch (error) {
        console.warn(`Unable to load ${language}; using English.`, error);
        language = "en";
        localizedNames = englishNames;
      }
      if (version !== renderVersion) return;
      const locale = language.replaceAll("_", "-");
      const direction = ["ar", "he"].includes(language) ? "rtl" : "ltr";
      const translate = (key) => localizedNames.get(key) || englishNames.get(key) || key;
      const navigation = document.createDocumentFragment();
      const content = document.createDocumentFragment();

      for (const category of categories) {
        const section = document.createElement("section");
        const heading = document.createElement("h2");
        heading.id = `category-${category.id}`;
        heading.textContent = translate(category.localizedNameKey);
        section.setAttribute("aria-labelledby", heading.id);
        section.append(heading);

        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent;
        item.append(link);
        navigation.append(item);

        const wallpapers = document.createElement("div");
        wallpapers.className = "wallpapers";

        for (const subcategory of [...category.subcategories].sort(byPreferredOrder)) {
          for (const asset of assets) {
            if (asset.categories.includes(category.id) && asset.subcategories.includes(subcategory.id)) {
              wallpapers.append(createWallpaper(asset, translate, locale));
            }
          }
        }

        if (wallpapers.childElementCount) {
          section.append(wallpapers);
        }

        content.append(section);
      }

      languagePicker.value = language;
      categoryList.lang = locale;
      categoryList.dir = direction;
      gallery.lang = locale;
      gallery.dir = direction;
      categoryList.replaceChildren(navigation);
      gallery.replaceChildren(content);
      categoryList.closest("nav").hidden = false;
      status.hidden = true;
    }

    languagePicker.addEventListener("change", () => {
      const url = new URL(window.location.href);
      url.searchParams.set("lang", languagePicker.value.replaceAll("_", "-"));
      window.history.pushState(null, "", url);
      render();
    });
    window.addEventListener("popstate", render);
    await render();
    languagePicker.disabled = false;

    if (window.location.hash) {
      const target = document.getElementById(window.location.hash.slice(1));
      target?.scrollIntoView();
    }
  } catch (error) {
    status.hidden = false;
    status.setAttribute("role", "alert");
    status.textContent = "Unable to load wallpapers. Please refresh to try again.";
    console.error(error);
  }
}

main();
