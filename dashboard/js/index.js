function renderHeatmapTab(selected) {

    'hide the toolip raised by the section chart'
    d3.select('#tooltip').style('opacity', 0)

    var radioButton,
        checkBox1,
        checkBox2,
        json;

    radioButton = selected;
    json = "./notebooks/confusionMatrixData.json"

    if (document.getElementById('nonNeurons').checked){
        checkBox1 = 'nonNeuronsOn'
    }
    else {
        checkBox1 = 'nonNeuronsOff'
    }


    if (document.getElementById('rangeDomain').checked){
        checkBox2 = 'rangeDomainOn'
    }
    else {
        checkBox2 = 'rangeDomainOff'
    }

    var confMatrixjson =    '.\\notebooks\\out\\' + radioButton +
                            '\\' + checkBox1 +
                            '\\' + checkBox2 +
                            '\\' + 'confusionMatrix.json';
    d3.json(confMatrixjson, function (data) {
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