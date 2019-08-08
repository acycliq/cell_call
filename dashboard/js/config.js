

function config(){
    var ini = [
        {
            name: '98 gene panel',
            roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457},
            imageSize: [16384, 11791],
            cellData: './dashboard/data/img/default_98genes/json/iss.json',
            geneData: './dashboard/data/img/default_98genes/json/Dapi_overlays.json',
            tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'
        },

        {
            name: 'default',
            roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457},
            imageSize: [16384, 11791],
            cellData: './dashboard/data/img/default/json/iss.json',
            geneData: './dashboard/data/img/default/json/Dapi_overlays.csv',
            tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'
        }, // 2

    ];

    var out = d3.map(ini, function (d) {return d.name;});
    return out
}




