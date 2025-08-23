Starplot uses a [Pydantic settings class](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to maintain a few global settings:

- Data download path
- DuckDB extension path
- SVG text rendering method

You can override these values in two ways: through code or through environment variables.

<h3>Code</h3>
To set values through code, just import the settings object:

```python
from starplot import settings

settings.svg_text_type = "element"

# Create your plot and enjoy your editable text :)

```

<h3>Environment Variables</h3>

To set values through environment variables, just add the `STARPLOT_` prefix to the setting name (and uppercase the entire name):

```shell

STARPLOT_DOWNLOAD_PATH=/home/myuser/downloads

```

::: starplot.config.Settings
    options:
        show_root_heading: true
        show_docstring_attributes: true
        separate_signature: true
        show_signature_annotations: true
        signature_crossrefs: true
        members: true

<hr/>

<br/><br/>
