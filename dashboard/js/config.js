

function config(){
    var ini = [
        {name: '99 gene panel', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/default_99genes/json/iss.json', geneData: './dashboard/data/img/default_99genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'}, // 2
        {name: '98 gene panel', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/default_98genes/json/iss.json', geneData: './dashboard/data/img/default_98genes/json/Dapi_overlays.json', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'}, // 2
        {name: 'Simulated spots (98 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,  // 4
        {name: 'Simulated spots (98 gene panel inc 10% nonDomestic fakes)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_10percFakeGenesNonDomestic/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_10percFakeGenesNonDomestic/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,  // 4
        {name: 'Simulated spots (98 gene panel inc 10% fakes)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_10percFakeGenes/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_10percFakeGenes/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,  // 4
        // {name: 'Simulated spots (98 gene panel) (Inefficiency: No shrink)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_98genes_noShrink/json/iss.json' , geneData: './dashboard/data/img/sim_123456_98genes_noShrink/csv/Dapi_overlays.csv' , tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'} ,
        {name: 'Simulated spots (62 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_62genes/json/iss.json', geneData: './dashboard/data/img/sim_123456_62genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'},  // 5
        {name: 'Simulated spots (42 gene panel)', roi: {x0: 6150, x1: 13751, y0: 12987, y1: 18457}, imageSize: [16384, 11791], cellData: './dashboard/data/img/sim_123456_42genes/json/iss.json', geneData: './dashboard/data/img/sim_123456_42genes/csv/Dapi_overlays.csv', tiles: './dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png'},  // 5
    ];
    var out = d3.map(ini, function (d) {return d.name;});
    return out
}




