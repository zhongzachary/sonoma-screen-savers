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

OUTPUT_PATH = OUTPUT_DIR / "localizations.json"

with LOCTABLE_PATH.open("rb") as f:
    LOCALIZATIONS = [
        {
            "language": language,
            "localizedNames": [
                {"key": key, "value": value} for key, value in localizedNames.items()
            ],
        }
        for language, localizedNames in plistlib.load(f).items()
        if language != "LocProvenance"
    ]


with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(LOCALIZATIONS, f, ensure_ascii=False, indent=2)

print(f"Saved {OUTPUT_PATH.name} to {OUTPUT_PATH}")
