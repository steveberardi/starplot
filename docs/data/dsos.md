Starplot has one officially supported catalog of deep sky objects (DSOs):

::: starplot.data.catalogs.OPEN_NGC
    options:
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true


<style>
    .md-content {
        max-width: 100%;
    }
</style>
<script src="https://unpkg.com/gridjs/dist/gridjs.umd.js"></script>
<link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />

The table below shows all the deep sky objects (DSOs) available in OpenNGC's database.

<div id="grid"></div>

<script>

    new gridjs.Grid({
        search: true,
        sort: true,
        pagination: {
            limit: 50
        },
        columns: [
            { 
                name: 'Name',
                formatter: (cell) => gridjs.html(`<b>${cell}</b>`),
            },
            'Type', 
            'RA',
            'DEC',
            'Magnitude',
            'Size (deg²)',
            'Geometry',
        ],
        server: {
            url: '/data/ongc.json',
            then: data => data.map(dso => [
                dso.name,
                dso.type,
                dso.ra,
                dso.dec,
                dso.magnitude,
                dso.size,
                dso.geom_type,
            ])
        } ,
        language: {
            'search': {
                'placeholder': '🔍 Search...'
            }
        },

    }).render(document.getElementById("grid"));

</script>

<br/><br/>
