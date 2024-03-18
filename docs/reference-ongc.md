<script src="https://unpkg.com/gridjs/dist/gridjs.umd.js"></script>
<link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />

The table below shows all the deep sky objects (DSOs) available through OpenNGC.

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
            // 'Size (deg2)',
            'Geometry',
        ],
        server: {
            url: '../data/ongc.json',
            then: data => data.map(dso => [
                dso.Name,
                dso.Type,
                dso.RA,
                dso.DEC,
                dso.Magnitude,
                // dso.Size,
                dso.Geometry,
            ])
        } ,
        language: {
            'search': {
                'placeholder': '🔍 Search...'
            }
        },

    }).render(document.getElementById("grid"));

</script>
