# 🌐 Translations

This directory contains the raw data that will be used in translating text in Starplot to other languages, including:

- Star names
- DSO names
- Constellation names (IAU-recognized constellations only, different constellations will be handled as part of sky cultures)
- Planet names
- Sun/moon
- Other terms (e.g. cardinal directions, legend, etc)

Each sub-directory stores a translation for a different language, with the directory name in [ISO-639-1 format](https://en.wikipedia.org/wiki/ISO_639-1).

The format of each file should be pretty self-explanatory, but here's a reference of the column names:

- `hip_id` = Hipparcos ID of a star
- `open_ngc_name` = Name of a DSO (as designated in OpenNGC)
- `iau_id` = Three letter IAU abbreviation of a constellation

## 🙋‍♂️ Help Wanted

If you're interested in helping with these translations (either finding and correcting errors or adding a new language), please open a PR with updates to these files.

Thanks for your help!

