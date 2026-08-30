# Projections

[Map plots](reference-mapplot.md) support a variety of projections, which are methods for flattening the curved, three-dimensional surface of a sphere (in Starplot, that's the sky) onto a two-dimensional flat surface like paper or a computer screen. Every projection is imperfect in some way because something will always be distorted. 

One of the common ways to visualize the distortions of a projection is by plotting [Tissot's indicatrix](https://en.wikipedia.org/wiki/Tissot's_indicatrix), which is a series of circles at various positions. Since they're actually circles on the surface of the sphere, you can see how that projection distorts objects by how much each circle looks distorted (i.e. more like an ellipse).

Projections in Starplot are ultimately handled by [PROJ](https://proj.org/en/stable/) (via [pyproj](https://pyproj4.github.io/pyproj/stable/)), but Starplot has thin wrappers for each projection that let you customize a few properties (e.g. central RA/DEC).

Below is a list of all projections supported by map plots, along with a Tissot indicatrix and available properties for each projection:

<div class="projection-card" markdown>


## Equidistant
Shows accurate distances from the center position. Often used for planispheres.
![Equidistant projection: gridlines and Tissot indicatrix](images/reference/projection_equidistant.svg){ width=400 loading=lazy }




</div>

<hr/>

<div class="grid cards feature-cards" markdown>

- __Equidistant__{.fs-2}
Shows accurate distances from the center position. Often used for planispheres.
![Equidistant projection: gridlines and Tissot indicatrix](images/reference/projection_equidistant.svg){ .projection-img loading=lazy }
- __LambertAzEqArea__{.fs-2}
Lambert Azimuthal Equal-Area projection - accurately shows area, but distorts angles.
![Lambert Azimuthal Equal-Area projection: gridlines and Tissot indicatrix](images/reference/projection_lambert_az_eq_area.svg){ .projection-img loading=lazy }
- __Mercator__{.fs-2}
Good for declinations between -70 and 70, but distorts objects near the poles
![Mercator projection: gridlines and Tissot indicatrix](images/reference/projection_mercator.svg){ .projection-img loading=lazy }
- __Miller__{.fs-2}
Similar to Mercator: good for declinations between -70 and 70, but distorts objects near the poles
![Miller projection: gridlines and Tissot indicatrix](images/reference/projection_miller.svg){ .projection-img loading=lazy }
- __Mollweide__{.fs-2}
Good for showing the entire celestial sphere in one plot
![Mollweide projection: gridlines and Tissot indicatrix](images/reference/projection_mollweide.svg){ .projection-img loading=lazy }
- __Robinson__{.fs-2}
Good for showing the entire celestial sphere in one plot
![Robinson projection: gridlines and Tissot indicatrix](images/reference/projection_robinson.svg){ .projection-img loading=lazy }
- __StereoNorth__{.fs-2}
Good for objects near the north celestial pole, but distorts objects near the mid declinations
![StereoNorth projection: gridlines and Tissot indicatrix](images/reference/projection_stereo_north.svg){ .projection-img loading=lazy }
- __StereoSouth__{.fs-2}
Good for objects near the south celestial pole, but distorts objects near the mid declinations
![StereoSouth projection: gridlines and Tissot indicatrix](images/reference/projection_stereo_south.svg){ .projection-img loading=lazy }
- __Stereographic__{.fs-2}
Similar to the North/South Stereographic projection, but allows custom central declination
![Stereographic projection: gridlines and Tissot indicatrix](images/reference/projection_stereographic.svg){ .projection-img loading=lazy }
- __PlateCarree__{.fs-2}
An equirectangular projection
![Plate Carree projection: gridlines and Tissot indicatrix](images/reference/projection_plate_carree.svg){ .projection-img loading=lazy }
- __ObliqueMercator__{.fs-2}
A cylindrical projection like Mercator, but the "cylinder" is wrapped around a specified great circle instead of the equator — you set that circle with center_ra/center_dec (a point on it) and azimuth (its direction there). This makes it useful for framing a narrow band of sky that runs at an angle to the RA/DEC grid — e.g. tracing the Milky Way's galactic plane, an eclipse path, or a satellite ground track — with low, Mercator-like distortion right along that line and shapes/angles preserved locally (it's conformal).
![Oblique Mercator projection: gridlines and Tissot indicatrix](images/reference/projection_oblique_mercator.svg){ .projection-img loading=lazy }
- __Orthographic__{.fs-2}
![Orthographic projection: gridlines and Tissot indicatrix](images/reference/projection_orthographic.svg){ .projection-img loading=lazy }
- __Gnomonic__{.fs-2}
![Gnomonic projection: gridlines and Tissot indicatrix](images/reference/projection_gnomonic.svg){ .projection-img loading=lazy }


</div>

## ::: starplot.Equidistant
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Equidistant projection: gridlines and Tissot indicatrix](images/reference/projection_equidistant.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.LambertAzEqArea
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Lambert Azimuthal Equal-Area projection: gridlines and Tissot indicatrix](images/reference/projection_lambert_az_eq_area.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.Mercator
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Mercator projection: gridlines and Tissot indicatrix](images/reference/projection_mercator.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.ObliqueMercator
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

## ::: starplot.Miller
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Miller projection: gridlines and Tissot indicatrix](images/reference/projection_miller.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.Mollweide
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Mollweide projection: gridlines and Tissot indicatrix](images/reference/projection_mollweide.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.PlateCarree
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Plate Carree projection: gridlines and Tissot indicatrix](images/reference/projection_plate_carree.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.Robinson
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Robinson projection: gridlines and Tissot indicatrix](images/reference/projection_robinson.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.Stereographic
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![Stereographic projection: gridlines and Tissot indicatrix](images/reference/projection_stereographic.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.StereoNorth
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![StereoNorth projection: gridlines and Tissot indicatrix](images/reference/projection_stereo_north.svg){ .off-glb .projection-img loading=lazy }

## ::: starplot.StereoSouth
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        heading_level: 2

![StereoSouth projection: gridlines and Tissot indicatrix](images/reference/projection_stereo_south.svg){ .off-glb .projection-img loading=lazy }
