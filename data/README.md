# data

The metadata for the screen savers is originally stored in 

> `
/Library/Application Support/com.apple.idleassetsd/Customer/entries.json
`

The file is copied to [entries.json](entries.json) for archiving purposes.

However, the [entries.json](entries.json) doesn't contain the name of the assets 
(and I was unable to locate the `localizable.strings` files for these asset.)
Hence, I manually compiled the names and ordering of the screen savers based on
my macBook's System Settings (set in en-US) and it is saved in [display_names.csv](display_names.csv).
