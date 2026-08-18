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

## Submitting a new translation

Please follow these steps in a pull request to submit a new translation:

1. Create a new directory here (`data/raw/translations`) with the name in [ISO-639-1 format](https://en.wikipedia.org/wiki/ISO_639-1)
2. In that new directory, create the following files (in the format of existing files):
    - `constellation_names.csv`
    - `dso_names.csv`
    - `other_terms.csv`
    - `star_names.csv`
3. Add the ISO-639-1 code to:
    - `LANGUAGES` list [here](https://github.com/steveberardi/starplot/blob/main/src/starplot/data/translations.py)
    - Doc-string for `Settings.language` [here](https://github.com/steveberardi/starplot/blob/main/src/starplot/config.py)
4. Copy the values from `other_terms.csv` to the `LABELS` dictionary [here](https://github.com/steveberardi/starplot/blob/main/src/starplot/data/translations.py)
5. Include a `readme.md` file in the data folder that explains the source of the translation (e.g. a well known astronomy book in the language, astronomical society, etc) - [see example here](https://github.com/steveberardi/starplot/blob/main/data/raw/translations/it/readme.md)

## Reviewing / fixing existing translations

If you spot an error or think there's a better translation for something in one of the existing translations, please let us know by submitting a PR with the correction, and including a source or explanation of the correction.

Thanks for your help!

