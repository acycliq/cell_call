

function config(){
    var ini = [
        {name: 'default', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/default/json/iss.json', geneData: './dashboard/data/img/default/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default/16384px/{z}/{x}/{y}.png'}, // 1
        {name: 'Simulation_1', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456/json/iss.json' , geneData: './dashboard/data/img/sim_123456/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default/16384px/{z}/{x}/{y}.png'} ,  // 2
        {name: 'Simulation_2', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_1549392942/json/iss.json', geneData: './dashboard/data/img/sim_1549392942/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default/16384px/{z}/{x}/{y}.png'},  // 3
    ];
    var out = d3.map(ini, function (d) {return d.name;});
    return out
}




