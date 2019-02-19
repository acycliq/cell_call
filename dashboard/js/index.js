function renderHeatmapTab(selected) {
    'hide the toolip raised by the section chart'
    d3.select('#tooltip').style('opacity', 0)

    if (selected == 'hybrid'){
        json = "./notebooks/confusionMatrixData.json"
    }
    else if (selected == 'satellite'){
        json = "./notebooks/confusionMatrixData.json"
    }
    else if (selected == 'basemap'){
        json = "./notebooks/confusionMatrixData.json"
    }
    else {
        json = ''
    }

    d3.json(json, function (data) {
        dataset = []
        for (var i = 0; i < data.index.length; i++) {
            // console.log(' i: ', i)
            for (var j = 0; j < data.columns.length; j++) {
                // console.log('i: ' + i + ' j: ' + j + ' value: ' + data.data[i][j])
                dataset.push({
                    xKey: i + 1,
                    xLabel: data.index[i],
                    yKey: j + 1,
                    yLabel: data.columns[j],
                    val: +data.data[i][j],
                })
            }
        }
        console.log('json parsed!!');
        renderHeatmap(dataset);
    });
}