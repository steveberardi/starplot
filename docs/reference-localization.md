
## Language

Starplot's labels are available in the following languages:

1. English (US) - default
2. Chinese
3. French
4. Lithuanian
5. Persian (Farsi)

**Want to see another language available?** Please help us add it! [Details here](https://github.com/steveberardi/starplot/tree/main/data/raw/translations)


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
