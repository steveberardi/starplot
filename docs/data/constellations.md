<script src="https://unpkg.com/gridjs/dist/gridjs.umd.js"></script>
<link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />

The table below shows all the constellations in Starplot's database, with their names and IAU id.

Note that Serpens is treated as two separate constellations in Starplot.

<div id="grid" class="constellations-data-grid"></div>

<script>

    new gridjs.Grid({
        search: true,
        sort: true,
        pagination: {
            limit: 50
        },
        columns: [
            'Name',
            'IAU id', 
        ],
        server: {
            url: '../constellations.json',
            then: data => data.map(c => [
                c.name,
                c.iau_id,
            ])
        } ,
        language: {
            'search': {
                'placeholder': '🔍 Search...'
            }
        },

    }).render(document.getElementById("grid"));

</script>
