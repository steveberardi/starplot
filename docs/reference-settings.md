# Settings

Starplot has a few global settings for things that affect all the plots you create:

- [Data path](#data_path)
- [Debug mode](#debug)
- [Language](#language)
- [Precision](#precision)
- [SVG text type](#svg_text_type)

You can set these values in two ways: through code or through environment variables:

<div class="grid" markdown>

```python title="Code"
from starplot import settings

settings.svg_text_type = "element"

# Create your plot and enjoy your editable text :)
```

```bash title="Environment Variables"
# To set values through environment variables, 
# just add the STARPLOT_ prefix to the setting 
# name (and uppercase the entire name):

STARPLOT_DATA_PATH=/home/myuser/data

```
</div>

---

## `data_path`

- Type: `str | Path`
- Default = _current working directory_

Path that Starplot will use for data and the DuckDB spatial extension, which is required for the data backend.


---

## `debug`

- Type: `bool`
- Default = `False`

Global setting for debug mode. When this is enabled, Starplot will log debugging information and plot polygons for debugging text issues

---

## `language`

- Type: `str`
- Default = `'en-us'`

Default language for plotted labels, as an ISO-639 code. Case insensitive.

Supported values:

- `en-us` = English (default)
- `es` = Spanish
- `fa` = Persian (Farsi). Make sure you have a Persian font installed that supports RTL (such as [Vazir](https://github.com/rastikerdar/vazir-font) or [Noto Sans Arabic](https://fonts.google.com/noto/specimen/Noto+Sans+Arabic)) and set it as the font in your plot's style.
- `fr` = French
- `it` = Italian
- `lt` = Lithuanian
- `nl` = Dutch
- `zh-cn` = Chinese. Make sure you have a good Chinese font installed (such as [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)) and you'll also need to set that as the font in your plot's style.
- `zh-tw` = Traditional Chinese

**🌐 Want to see another language available? Please help us add it! [Details here](https://github.com/steveberardi/starplot/tree/main/data/raw/translations).**

---

## `precision`

- Type: `int`
- Default = `4`

Number of decimal places to round coordinates and dimensions to when rendering SVG output.

---

## `svg_text_type`

- Type: `str`
- Default = `'element'`
- Method for rendering text in SVG exports:
    - `"path"` (default) will render all text as paths. This will increase the filesize, but allow all viewers to see the font correctly (even if they don't have the font installed on their system).
    - `"element"` will render all text as an [SVG `<text>` element](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/text), which means the text will be editable in graphic design applications but the text may render in a system default font if the original font isn't available.


<!-- 
::: starplot.config.Settings
    options:
        show_docstring_attributes: true
        separate_signature: true
        show_signature_annotations: true
        signature_crossrefs: true
        members: true -->

<hr/>

<br/><br/>
