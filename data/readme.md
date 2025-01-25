
# Starplot Data

This folder contains all the raw data and scripts Starplot uses to build its database file: `sky.db`

# In a nutshell

### `make db`
- Builds data assets and writes them to `build/`
- Creates the `sky.db` database from the build files
- Copies `sky.db` to Starplot's data library, which will get distributed with the Python package

# Need to update data?

1. Update values in `raw/`
2. Update data scripts if required
3. Run `make db`
