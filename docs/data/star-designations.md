<script src="https://unpkg.com/gridjs/dist/gridjs.umd.js"></script>
<link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />

The table below shows all the star designations in Starplot's database, by their Hipparcos (HIP) id.

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
                name: 'HIP',
                formatter: (cell) => gridjs.html(`<strong>${cell}</strong>`),
            },
            'Name',
            'Bayer', 
            'Flamsteed',
        ],
        server: {
            url: '../star_designations.json',
            then: data => data.map(star => [
                star.hip,
                star.name,
                star.bayer,
                star.flamsteed,
            ])
        } ,
        language: {
            'search': {
                'placeholder': '🔍 Search...'
            }
        },

    }).render(document.getElementById("grid"));

</script>
