# Style Extensions

Starplot has many built-in style extensions for different color schemes, plot types, and gradient backgrounds.

Using them is pretty simple:

```python
from starplot import styles

style = styles.PlotStyle().extend(
    styles.extensions.BLUE_GOLD,
    styles.extensions.GRADIENT_PRE_DAWN,
)
```

- **Color Schemes**
    - `GRAYSCALE` - Optimized for printing in grayscale ([details](#extensions-grayscale))
    - `GRAYSCALE_DARK` - Like `GRAYSCALE`, but inverted (white stars, black background) ([details](#extensions-grayscale-dark))
    - `BLUE_LIGHT` - Light and bright colors ([details](#extensions-blue-light))
    - `BLUE_MEDIUM` - Medium brightness bluish gray colors ([details](#extensions-blue-medium))
    - `BLUE_DARK` - Dark "Starplot blue" colors ([details](#extensions-blue-dark))
    - `BLUE_GOLD` - Dark blue / gold colors ([details](#extensions-blue-gold))
    - `BLUE_NIGHT` - Very dark blue background with colored markers ([details](#extensions-blue-night))
    - `ANTIQUE` - Antique map inspired colors ([details](#extensions-antique))
    - `NORD` - Nord-inspired colors ([details](#extensions-nord))
- **Plot types**
    - `OPTIC` - Basic styling tailored for optic plots ([details](#extensions-optic))
    - `MAP` - Basic styling tailored for map plots ([details](#extensions-map))
    - `PUBLICATION` - Styling rules tailored for plots that will be imported to design applications ([details](#extensions-publication))
- **Gradients**
    - `GRADIENT_DAYLIGHT`
    - `GRADIENT_BOLD_SUNSET`
    - `GRADIENT_CIVIL_TWILIGHT`
    - `GRADIENT_NAUTICAL_TWILIGHT`
    - `GRADIENT_ASTRONOMICAL_TWILIGHT`
    - `GRADIENT_TRUE_NIGHT`
    - `GRADIENT_PRE_DAWN`
    - `GRADIENT_OPTIC_FALLOFF`
    - `GRADIENT_OPTIC_FALL_IN`

<!-- GRAYSCALE -->
<h2 class="doc doc-heading" id="extensions-grayscale"><code>GRAYSCALE</code></h2>

<div class="indent" markdown>
Optimized for printing in grayscale

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/grayscale.yml"
    ```
</div>

<!-- GRAYSCALE DARK -->
<h2 class="doc doc-heading" id="extensions-grayscale-dark"><code>GRAYSCALE_DARK</code></h2>

<div class="indent" markdown>
Like `GRAYSCALE`, but inverted (white stars, black background)

???- star "Source"

    ```yaml
    --8<-- "src/starplot/styles/ext/grayscale_dark.yml"
    ```
</div>

<!-- BLUE LIGHT -->
<h2 class="doc doc-heading" id="extensions-blue-light"><code>BLUE_LIGHT</code></h2>

<div class="indent" markdown>
Light and bright colors

???- star "Source"

    ```yaml
    --8<-- "src/starplot/styles/ext/blue_light.yml"
    ```
</div>

<!-- BLUE MEDIUM -->
<h2 class="doc doc-heading" id="extensions-blue-medium"><code>BLUE_MEDIUM</code></h2>

<div class="indent" markdown>
Medium brightness bluish gray colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_medium.yml"
    ```
</div>

<!-- BLUE DARK -->
<h2 class="doc doc-heading" id="extensions-blue-dark"><code>BLUE_DARK</code></h2>

<div class="indent" markdown>
Dark bluish gray colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_dark.yml"
    ```
</div>

<!-- BLUE GOLD -->
<h2 class="doc doc-heading" id="extensions-blue-gold"><code>BLUE_GOLD</code></h2>

<div class="indent" markdown>
Dark bluish gold colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_gold.yml"
    ```
</div>

<!-- BLUE NIGHT -->
<h2 class="doc doc-heading" id="extensions-blue-night"><code>BLUE_NIGHT</code></h2>

<div class="indent" markdown>
Very dark blue background with colored markers

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_night.yml"
    ```
</div>

<!-- ANTIQUE -->
<h2 class="doc doc-heading" id="extensions-antique"><code>ANTIQUE</code></h2>

<div class="indent" markdown>
Antique map inspired colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/antique.yml"
    ```
</div>

<!-- NORD -->
<h2 class="doc doc-heading" id="extensions-nord"><code>NORD</code></h2>

<div class="indent" markdown>
Nord inspired colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/nord.yml"
    ```
</div>

<!-- OPTIC -->
<h2 class="doc doc-heading" id="extensions-optic"><code>OPTIC</code></h2>

<div class="indent" markdown>
Basic styling tailored for optic plots

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/optic.yml"
    ```
</div>

<!-- MAP -->
<h2 class="doc doc-heading" id="extensions-map"><code>MAP</code></h2>

<div class="indent" markdown>
Basic styling tailored for map plots

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/map.yml"
    ```
</div>


<!-- PUBLICATION -->
<h2 class="doc doc-heading" id="extensions-publication"><code>PUBLICATION</code></h2>

<div class="indent" markdown>
Styling rules tailored for plots that will be imported to design applications

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/publication.yml"
    ```
</div>
