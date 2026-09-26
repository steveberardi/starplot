## Project
Starplot is a Python library for creating star charts and maps of the sky.

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
- `data/` - Raw data for star names and translations
- `plots/` - Scratch code for local development

## Commands
- Test: `make test`
- Format: `make format`
- Lint: `make lint`

## Verification
After every change, run in this order:
1. [Test command] — fix failing tests if they're failing because of your change
2. [Format command] - fix formatting
3. [Lint command] — fix lint errors
DO NOT run the hash checks unless specifically told to do so

## Conventions
- When creating plots for research or investigating an issue:
    - Put the source code in the `claude/` directory 
    - Put the output of the final plot in `claude/output/`
    - Prefer SVG output, unless told otherwise
- Avoid comments that only describe what the code does (unless it's a docstring for a function)
- When it's not obvious why code does something a certain way, then a comment explaining _why_ should be added
- When writing tests, avoid mocking things when possible. 
- HTTP requests should always be mocked in tests, but their mocked response should mimic the data structure of the real response
- When finishing a code task, include a bulleted list of files you modified and make them links to open in VSCode
