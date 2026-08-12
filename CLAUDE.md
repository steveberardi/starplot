## Project
Starplot — a Python library for creating star charts and maps of the sky.

## Important Dependencies
- Python
- pyproj
- skyfield
- shapely
- pydantic
- astropy
- ibis-framework
- fonttools
- cairosvg

## Structure
- `src/` — All source code for the distributed Starplot library
- `tests/` — All unit tests
- `hash_checks/` — Image hash tests that confirm plots are created correctly
- `examples/` — Example code for various plots, used on the documentation website
- `tutorial/` - Code for the tutorial, used on the documentation website
- `docs/` — Documentation files (using Zensical for building)
- `data/` - Raw data for star names, and translations
- `plots/` - Scratch code for local development

## Commands
- Test: `make test`
- Format: `make format`
- Lint: `make lint`

## Verification
After every change, run in this order:
1. [Test command] — fix failing tests
2. [Format command] - fix formatting
3. [Lint command] — fix lint errors

## Conventions
- When creating plots for research or investigating an issue:
    - Put the source code in the `plots/` directory 
    - Put the output of the final plot in `plots/output/`
    - Prefer SVG output, unless told otherwise
- Avoid comments that only describe what the code does. Instead, focus on writing comments that explain _why_ the code does something.
