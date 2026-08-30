<style>
.sub-header {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--md-default-fg-color--light);
    margin: 32px 0 8px;
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
    border-bottom: 1px solid var(--md-default-fg-color--lightest);
}

.projection-card {
    padding: 28px;
    margin-bottom: 20px;
    background-color: var(--muted-bg-color);
    border-radius: 8px;
    display: grid;
    grid-template-columns: 2fr 1.5fr;
    gap: 24px;

    ul {
        margin: 0px !important;
        font-family: "Fira Code", var(--md-code-font-family);
    }

    ul li {
        margin-left: 0px !important;
        list-style-type: none;
        margin-top: 4px;
        font-size: 13px;
    }

    h3 {
        color: var(--md-primary-fg-color);
        font-weight: 700;
        font-size: 1.35rem;
        margin-top: 0;
    }

    h4, h5 {
        font-weight: 500;
        letter-spacing: 0.07rem;
        margin-bottom: 0;
        margin-top: 20px;
    }

    h2, h3, h4, h5 {
        font-family: "Fira Code", var(--md-code-font-family);
        
    }

    img {
        max-width: 340px;
    }

    .proj-link {
        margin-top: 20px;
        margin-bottom: 0;
    }

    .proj-link a {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
    }
}


</style>

# Projections

[Map plots](reference-mapplot.md) support a variety of projections, which are methods for flattening the curved, three-dimensional surface of a sphere (in Starplot, that's the sky) onto a two-dimensional flat surface like paper or a computer screen. Every projection is imperfect in some way because something will always be distorted. 

Projections in Starplot are ultimately handled by [PROJ](https://proj.org/en/stable/) (via [pyproj](https://pyproj4.github.io/pyproj/stable/)), but Starplot has thin wrappers for each projection that let you customize a few properties (e.g. central RA/DEC).

**Basic Usage**
<div class="tutorial">
```python
from starplot import MapPlot, Stereographic

p = MapPlot(
    dec_min=-20,
    dec_max=90,
    projection=Stereographic(  # create a Stereographic projection with a custom center RA/DEC 
        center_ra=250, 
        center_dec=35,
    )
)
```
</div>

Below is a list of all projections supported by map plots, along with a [Tissot's indicatrix](https://en.wikipedia.org/wiki/Tissot's_indicatrix) for each projection to illustrate how it distorts objects:

--8<-- "docs/images/reference/projection_list.html"


<br/><br/><br/>
