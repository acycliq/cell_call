

function config(){
    var ini = [
        {name: '99 gene panel', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/default_99genes/json/iss.json', geneData: './dashboard/data/img/default_99genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'}, // 2
        {name: '98 gene panel', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/default_98genes/json/iss.json', geneData: './dashboard/data/img/default_98genes/json/Dapi_overlays.json', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'}, // 2
        // {name: 'Simulated spots (98 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,  // 4
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 1.0)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency1.0/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency1.0/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,  // 4
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 0.5)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency0.5/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency0.5/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 0.25)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency0.25/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency0.25/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 0.12)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency0.12/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency0.12/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 0.06)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency0.06/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency0.06/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (98 gene panel) (Inefficiency: 0.03)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_inefficiency0.03/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_inefficiency0.03/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (62 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_62genes/json/iss.json', geneData: './dashboard/data/img/sim_123456_62genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'},  // 5
        {name: 'Simulated spots (42 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_42genes/json/iss.json', geneData: './dashboard/data/img/sim_123456_42genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'},  // 5
    ];
    var out = d3.map(ini, function (d) {return d.name;});
    return out
}




