# data

The metadata for the screen savers is originally stored in 

`~/Library/Application Support/com.apple.wallpaper/aerials/manifest/entries.json`

The localized string file is stored in
`~/Library/Application Support/com.apple.wallpaper/aerials/manifest/TVIdleScreenStrings.bundle/Contents/Resources/Localizable.nocache.loctable`

Run collect_data.py will:
- copy the `entries.json` into this folder, and
- parse the `.loctable` file and save as `localizations.json`.

To refresh the data, run the following in the project directory

```zsh
uv run data/collect_data.py
```
