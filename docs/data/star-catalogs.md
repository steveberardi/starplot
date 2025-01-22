Starplot has two available star catalogs:

## `big-sky-mag11`

_981,852 stars from Hipparcos, Tycho-1, and Tycho-2_

This is an abridged version of the full [Big Sky Catalog](https://github.com/steveberardi/bigsky) and is bundled with Starplot. It's the default catalog used when plotting stars. It contains all stars from Big Sky with a limiting magnitude of 11.


## `big-sky`

_2,557,500 stars from Hipparcos, Tycho-1, and Tycho-2_

This is the full Big Sky catalog and will be downloaded when you first reference it.

This catalog is very large (approx 100 MB), so it's not built-in to Starplot. When you plot stars and specify this catalog, the catalog 
will be downloaded from the [Big Sky GitHub repository](https://github.com/steveberardi/bigsky) and saved to Starplot's data library 
directory. You can override this download path with the environment variable `STARPLOT_DOWNLOAD_PATH`


!!! star "Coming Soon"

    Support for custom star catalogs, including the full Gaia catalog!


## Using Star Catalogs

When plotting stars, you can specify which catalog to use:

<div class="tutorial">
```python
p.stars(
    where=[_.magnitude < 12],
    catalog="big-sky",          # <--- use the full Big Sky catalog
)
```
</div>

You can also specify the catalog when looking up stars:

<div class="tutorial">
```python

# get a single star
sirius = Star.get(name="Sirius", catalog="big-sky")

# get stars dimmer than magnitude 11
dim_stars = Star.find(where=[_.magnitude > 11], catalog="big-sky")

```
</div>

<br/><br/><br/>