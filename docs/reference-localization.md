
## Language

Starplot's labels have been translated for the following languages:

1. French
2. Chinese

By default, labels are plotted in English (`en-US`).

*For Chinese, make sure you have a good Chinese font installed (such as [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)) and you'll also need to set that as the font in your plot's style.

!!! star "Want to see another language available?"
    Please help us add it! [Details here](https://github.com/steveberardi/starplot/tree/main/data/raw/translations)


!!! tip "How to Use a Different Language"

    The language in Starplot is configured by a [global setting](reference-settings.md), which you can set via environment variables or via the settings object directly.


    Example:

    <div class="tutorial">

    ```python

    from starplot import ZenithPlot, settings

    settings.language = "fr" # set the language to French

    zp = ZenithPlot(...)

    zp.stars(where=[_.magnitude < 6]) # labels for these stars will be in French

    ```

    </div>

<br/><br/>
