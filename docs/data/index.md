# Data Catalogs - Overview

Starplot has a [Catalog][starplot.data.Catalog] class that represents a catalog of sky objects. They're currently supported for the following object types:  stars, constellations, and deep sky objects (DSOs).

There are a few officially supported catalogs for each object type, but you can also [build your own](building.md). When you first plot an object type with a catalog, if the catalog path doesn't already exist and the catalog has a URL defined then it'll be downloaded from that URL. All the offically supported catalogs have download URLs.

All catalogs are stored as [Parquet](https://www.datacamp.com/tutorial/apache-parquet) files to allow fast object lookup.


::: starplot.data.Catalog
    options:
        members_order: source
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true


::: starplot.data.catalogs.SpatialQueryMethod
    options:
        members_order: source
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true


---


<br/><br/><br/>


