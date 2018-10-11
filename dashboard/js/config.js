

function config(){
    var ini = [
        {name: 'default', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [65536, 47168], cellData: './dashboard/data/img/default/json/iss.json', geneData: './dashboard/data/img/default/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default/65536px/{z}/{x}/{y}.png'},
        {name: '161220KI_3-1_left', roi: {x0: 4133, x1: 10262, y0: 12578, y1: 18125}, imageSize: [65536, 59314], cellData: './dashboard/data/img/DapiBoundaries_161220KI_3-1_left/json/iss.json', geneData: './dashboard/data/img/DapiBoundaries_161220KI_3-1_left/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/DapiBoundaries_161220KI_3-1_left/65536px/{z}/{x}/{y}.png'},
        {name: '161220KI_3-1_right', roi: {x0: 21329, x1: 27597, y0: 11563, y1: 17575}, imageSize: [65536, 62860], cellData: './dashboard/data/img/DapiBoundaries_161220KI_3-1_right/json/iss.json', geneData: './dashboard/data/img/DapiBoundaries_161220KI_3-1_right/csv/Dapi_overlays.csv', tiles: "./dashboard/data/img/DapiBoundaries_161220KI_3-1_right/65536px/{z}/{x}/{y}.png"},
        // {name: '161220KI_3-2_left_20180706', roi: {x0: 6252, x1: 11826, y0: 13585, y1: 17303}, },
    ];
    var out = d3.map(ini, function (d) {return d.name;});
    return out
}
