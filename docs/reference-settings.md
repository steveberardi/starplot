Starplot has a few global settings:

- Data path
- Language
- SVG text rendering method

You can override these values in two ways: through code or through environment variables.

<h3>Code</h3>
To set values through code, just import the settings object:

```python
from starplot import settings

settings.svg_text_type = "element"

# Create your plot and enjoy your editable text :)

```

There's also a context manager that lets you temporarily override settings:

```python
from starplot import override_settings

with override_settings(language="zh-cn"):
    ...
    # all default labels plotted in here will be in Chinese

# after exiting the context manager, language will revert to the default (en-us)

```

<h3>Environment Variables</h3>

To set values through environment variables, just add the `STARPLOT_` prefix to the setting name (and uppercase the entire name):

```shell

STARPLOT_DATA_PATH=/home/myuser/data

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
