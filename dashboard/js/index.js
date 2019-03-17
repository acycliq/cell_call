function renderHeatmapTab(selected) {

    'hide the toolip raised by the section chart'
    d3.select('#tooltip').style('opacity', 0)

    var radioButton,
        checkBox0,
        checkBox1,
        checkBox2,
        json;

    radioButton = selected; // mean or median?
    json = "./notebooks/confusionMatrixData.json"

    if (document.getElementById('genes42').checked) {
        checkBox0 = '42genes'
    }
    else if (document.getElementById('genes62').checked)
    {
        checkBox0 = '62genes'
    }
    else {
        checkBox0 = '98genes'
    }

    if (document.getElementById('nonNeurons').checked) {
        checkBox1 = 'nonNeuronsOn'
    } else {
        checkBox1 = 'nonNeuronsOff'
    }


    if (document.getElementById('rangeDomain').checked) {
        checkBox2 = 'rangeDomainOn'
    } else {
        checkBox2 = 'rangeDomainOff'
    }

    var confMatrixjson =    '.\\notebooks\\jsonFiles\\' + checkBox0 +
                            '\\' + checkBox2 +
                            '\\' + radioButton +
                            '\\' + checkBox1 +
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


var sectionChartFilters = document.getElementById('section-chart-controls');
var checkItAll = sectionChartFilters.querySelector('input[name="cb:select-all"]');
var clearItAll = sectionChartFilters.querySelector('input[name="cb:clear-all"]');
var inputs = sectionChartFilters.querySelectorAll('tbody>tr>td>input:not([name="cb:select-all"]):not([name="cb:clear-all"])');
var other = sectionChartFilters.querySelector('input[name="cb:other"]');


inputs.forEach(function (input) {
    input.addEventListener('change', function () {
        if (!this.checked) {
            checkItAll.checked = false;
            checkItAll.disabled = false;
        }
        if (this.checked) {
            clearItAll.checked = false;
            clearItAll.disabled = false;
        }
        if (!checkItAll.checked) {
            var allChecked = true;
            for (var i = 0; i < inputs.length; i++) {
                if (!inputs[i].checked) {
                    allChecked = false;
                }
            }

            if (allChecked) {
                checkItAll.checked = true;
                checkItAll.disabled = true;
                clearItAll.disabled = false;
                clearItAll.checked = false;
            }
        }

        var selected = getSelected(inputs),
            filteredSectionData = cellData.filter(function (el) {
            var it = selected.includes(el.managedData.IdentifiedType);
            if (input.name === 'Other'){
                return !it
            }
            else {
                return it
            }
        });
        sectionChart(filteredSectionData)
    });

});


checkItAll.addEventListener('change', function () {
    inputs.forEach(function (input) {
        input.checked = checkItAll.checked;
    });
    checkItAll.disabled = true;
    clearItAll.disabled = false;
    clearItAll.checked = false;

    var selected = getSelected(inputs),
        filteredSectionData = cellData.filter(function (el) {
            return selected.includes(el.managedData.IdentifiedType);
        });
    sectionChart(filteredSectionData)
});


clearItAll.addEventListener('change', function () {
    inputs.forEach(function (input) {
        input.checked = !clearItAll.checked;
    });
    checkItAll.checked = false;
    checkItAll.disabled = false;
    clearItAll.disabled = true;

    var selected = getSelected(inputs),
        filteredSectionData = cellData.filter(function (el) {
            return selected.includes(el.managedData.IdentifiedType);
        });
    sectionChart(filteredSectionData)
});

function getSelected(inputs) {
    //Loop over all selected
    var selected = [];
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            if (inputs[i].name === 'Cck') {
                selected.push('Cck Calb1/Slc17a8*', 'Cck Cxcl14-', 'Cck Cxcl14+', 'Cck Vip Cxcl14-', 'Cck Vip Cxcl14+');
            } else if (inputs[i].name === 'PC') {
                selected.push('PC', 'PC Other1', 'PC Other2')
            } else if (inputs[i].name === 'IS') {
                selected.push('IS1', 'IS2', 'IS3')
            }
            else {
                selected.push(inputs[i].name);
            }
        }
    }
    return selected
}