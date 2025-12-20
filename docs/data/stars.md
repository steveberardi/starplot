Starplot has two officially supported star catalogs:

::: starplot.data.catalogs.BIG_SKY
    options:
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true

---

::: starplot.data.catalogs.BIG_SKY_MAG11
    options:
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true

---

## Using Star Catalogs

When plotting stars, you can specify which catalog to use:

<div class="tutorial">
```python
from starplot.data.catalogs import BIG_SKY

p.stars(
    where=[_.magnitude < 12],
    catalog=BIG_SKY,          # <--- use the full Big Sky catalog
)
```
</div>

You can also specify the catalog when looking up stars:

<div class="tutorial">
```python
from starplot.data.catalogs import BIG_SKY

# get a single star
sirius = Star.get(name="Sirius", catalog=BIG_SKY)

# get stars dimmer than magnitude 11
dim_stars = Star.find(where=[_.magnitude > 11], catalog=BIG_SKY)

```
</div>

<br/><br/><br/>