import json
import plistlib
import shutil
from pathlib import Path

MANIFEST_DIR = Path(
    "~/Library/Application Support/com.apple.wallpaper/aerials/manifest"
).expanduser()

OUTPUT_DIR = Path(__file__).parent

# Copy entries.json if it exists
ENTRIES_PATH = MANIFEST_DIR / "entries.json"
if ENTRIES_PATH.exists():
    output_path = OUTPUT_DIR / "entries.json"
    shutil.copy2(ENTRIES_PATH, output_path)
    print(f"Saved {ENTRIES_PATH.name} to {output_path}")

# Parse localization table
LOCTABLE_PATH = (
    MANIFEST_DIR
    / "TVIdleScreenStrings.bundle/Contents/Resources/Localizable.nocache.loctable"
)

LOCALES_DIR = OUTPUT_DIR / "locales"

with LOCTABLE_PATH.open("rb") as f:
    LOCALIZATIONS = {
        locale: localized_names
        for locale, localized_names in plistlib.load(f).items()
        if locale != "LocProvenance"
    }

LOCALES_DIR.mkdir(parents=True, exist_ok=True)
for locale, localized_names in LOCALIZATIONS.items():
    normalized_locale = locale.replace("_", "-")
    output_path = LOCALES_DIR / f"{normalized_locale}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "locale": normalized_locale,
                "localizedStrings": localized_names,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Saved {locale} to {output_path}")
