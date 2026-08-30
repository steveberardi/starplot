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
    grid-template-columns: 2fr 2fr;
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
        font-weight: 700;
        font-size: 1.2rem;
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

    
}


</style>

# Projections

[Map plots](reference-mapplot.md) support a variety of projections, which are methods for flattening the curved, three-dimensional surface of a sphere (in Starplot, that's the sky) onto a two-dimensional flat surface like paper or a computer screen. Every projection is imperfect in some way because something will always be distorted. 

Projections in Starplot are ultimately handled by [PROJ](https://proj.org/en/stable/) (via [pyproj](https://pyproj4.github.io/pyproj/stable/)), but Starplot has thin wrappers for each projection that let you customize a few properties (e.g. central RA/DEC).

!!! example "Basic Usage"
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


Below is a list of all projections supported by map plots, along with a [Tissot's indicatrix](https://en.wikipedia.org/wiki/Tissot's_indicatrix) for each projection to illustrate how it distorts objects:
<!-- 
One of the common ways to visualize the distortions of a projection is by plotting [Tissot's indicatrix](https://en.wikipedia.org/wiki/Tissot's_indicatrix), which is a series of circles at various positions. Since they're actually circles on the surface of the sphere, you can see how that projection distorts objects by how much each circle looks distorted (i.e. more like an ellipse). -->

<div class="projection-card">
    <div>
        <h3>Equidistant</h3>
        <p>Shows accurate distances from the center position. Often used for planispheres.</p>
        <div class="sub-header">Properties</div>
        <ul>
            <li>center_ra</li>
            <li>center_dec</li>
        </ul>
    </div>
    <img src="images/reference/projection_equidistant.svg" width=400 />
</div>

<div class="projection-card">
    <div>
        <h3>LambertAzEqArea</h3>
        <p>Lambert Azimuthal Equal-Area projection - accurately shows area, but distorts angles.</p>
        <div class="sub-header">Properties</div>
        <ul>
            <li>center_ra</li>
            <li>center_dec</li>
        </ul>
    </div>
    <img src="images/reference/projection_lambert_az_eq_area.svg" width=400 />
</div>






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
