var menuSelection,
    cm_dataset;  // Another one in the global scope!


var non_neuron = ['Astro.1',
                 'Astro.2',
                 'Astro.3',
                 'Astro.4',
                 'Astro.5',
                 'Choroid',
                 'Endo',
                 'Eryth.1',
                 'Eryth.2',
                 'Microglia.1',
                 'Microglia.2',
                 'Oligo.1',
                 'Oligo.2',
                 'Oligo.3',
                 'Oligo.4',
                 'Oligo.5',
                 'Vsmc'
                 ];

function renderHeatmapTab(menuSelection) {

    // hide the toolip raised by the section chart
    d3.select('#tooltip').style('opacity', 0);

    d3.csv(menuSelection.target_file, function(data){
        cm_dataset = heatmapDataManager(data, menuSelection.norm, +menuSelection.foldVal);
        console.log('data from '+ menuSelection.target_file + ' fed into the confusion matrix');
        renderHeatmap(cm_dataset, '#heat-chart');
        var diagonalScore = diagonalMean(cm_dataset);
        cmAnalytics(diagonalScore)
    })
}


// Update now table on the confusion matrix tab with the analytics results
function cmAnalytics(score) {
    // check if a there is a reference to a datatable.
    // If yes, refresh with the new data
    // Otherwise create and populate a datatable
    if ($.fn.dataTable.isDataTable('#cm_analytics')) {
        table = $('#cm_analytics').DataTable();
        table.clear().rows.add(score).draw();
    } else {
        table = $('#cm_analytics').DataTable({
            "lengthChange": false,
            searching: false,
            "paging": false,
            "bPaginate": false,//Dont want paging
            "bInfo": false, //Dont display info e.g. "Showing 1 to 4 of 4 entries"
            "data": score,
            "columns": [
                    {
                        title: "Metric",
                        data: "metric"
                    },
                    {
                        title: "Value",
                        data: "value"
                    }
                ],
        });

    }
}

var sectionChartFilters = document.getElementById('section-chart-controls');
var checkItAll = sectionChartFilters.querySelector('input[name="cb:select-all"]');
var clearItAll = sectionChartFilters.querySelector('input[name="cb:clear-all"]');
var inputs = sectionChartFilters.querySelectorAll('tbody>tr>td>input:not([name="cb:select-all"]):not([name="cb:clear-all"])');
var other = sectionChartFilters.querySelector('input[name="cb:other"]');


inputs.forEach(function (input) {
    input.addEventListener('change', function () {
        // first of all, hide the existing tooltip
        d3.select('#tooltip').style('opacity', 0);

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
                if (input.name === 'Other') {
                    return !it
                } else {
                    return it
                }
            });
        sectionChart(filteredSectionData)
    });

});


checkItAll.addEventListener('change', function () {
    // first of all, hide the existing tooltip
    d3.select('#tooltip').style('opacity', 0);

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
    // first of all, hide the existing tooltip
    d3.select('#tooltip').style('opacity', 0);

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
            } else {
                selected.push(inputs[i].name);
            }
        }
    }
    return selected
}


function sortObjects(array) {
    let keys;

    function _sort(obj) {
        if (!keys) {
            keys = Object.keys(obj);
            return obj;
        }
        return keys.reduce((sorted, key) => {
            sorted[key] = obj[key];
            return sorted;
        }, {})
    }

    return array.map(_sort);
}


function heatmapDataManager(data, norm, ddl) {
// Helper function to handle the data to be fed in to heatmap
// ddl is the drill down level. Data are aggregated over that level.
// For example 'Astro.1', 'Astro.2' ,..., 'Astro.5' will all be combined
// in a big class 'Astro' if ddl=1
// norm is either 'avg' or 'median'. The default is 'median'

    function stripper(d, k) {
        for (i = 0; i < k; ++i) {
            if (d.lastIndexOf('.') > 0) {
                d = d.substring(0, d.lastIndexOf('.'))
            }
        }
        return d
    }


    // if you select to group the NonNeurons, this is where grouping happens
    if (document.getElementById("nonNeurons").checked) {
        console.log('Grouping non neurons together')
        var data = data.map(o => Object.entries(o).reduce((o, [k, v]) => {
            //const firsts = k => k.split('.').slice(0, -1).join('.');
            if (k === 'model_class') {
                o[k] = non_neuron.includes(v) ? 'NonNeuron' : v;
            } else {
                k = non_neuron.includes(k) ? 'NonNeuron' : k;
                o[k] = (o[k] || 0) + parseFloat(v);
            }
            return o;
        }, {}));
    }


    // var ddl = 4; //drill down level
    var result = data.map(o => Object.entries(o).reduce((o, [k, v]) => {
        //const firsts = k => k.split('.').slice(0, -1).join('.');
        if (k === 'model_class') {
            o[k] = stripper(v, ddl);
        } else {
            k = stripper(k, ddl);
            o[k] = (o[k] || 0) + parseFloat(v);
        }
        return o;
    }, {}));


    var out = d3.nest()
        .key(function (d) {
            return d.model_class;
        })
        .rollup(function (v) {
            var teams = v.map(function (team) {
                delete team.model_class;
                return d3.entries(team);
            }).reduce(function (memo, team) {
                return memo.concat(team);
            }, []);

            var a = d3.nest()
                .key(function (d) {
                    return d.key;
                })
                .rollup(function (w) {
                    return {
                        count: w.length,
                        median: d3.median(w, function (d) {
                            return d['value'];
                        }),
                        avg: d3.mean(w, function (d) {
                            return d['value'];
                        })
                    };
                })
                .entries(teams);

            return a;
        })
        .entries(result);


    dataset = [];
    for (var i = 0; i < out.length; i++) { //62
        // console.log(' i: ', i)
        var cur = out[i],
            curKey = cur.key, // this is the model_class
            curVal = cur.value;
        for (var j = 0; j < curVal.length; j++) { //71
            // console.log('i: ' + i + ' j: ' + j + ' value: ' + data.data[i][j])
            dataset.push({
                xKey: j + 1,
                xLabel: curVal[j].key,
                yKey: i + 1,
                yLabel: cur.key,
                val: norm === 'avg'? +curVal[j].value.avg: // check if you want the avg
                        norm === 'median'? +curVal[j].value.median: //else check if you want the median
                            '',                                     // else return an empty string. You should not get this deep.
            })
        }
    }


    return dataset
}

// listener on the Confusion matrix tab
$('#layers-base input').change(function () {
    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-2 input').change(function () {
    console.log('Group non neurons was clicked')
    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-3 input').change(function () {
    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-4 input').change(function () {
    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-5 input').change(function () {
    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-6 input').change(function () {
    var target = submitHelper();
    renderHeatmapTab(target)
});


// listener on the Confusion matrix tab
$('#confusion-table-tab').on('shown.bs.tab', function (e) {
    console.log('Confusion matrix tab was clicked.');
    // hide the navbar dropdown menus
    $('#myDropdown').hide();
    $('#myDropdown2').hide();
    var target = submitHelper();
    renderHeatmapTab(target)
});

// listener on the Viewer tab
$('#map-tab').on('shown.bs.tab', function (e) {
    console.log('Viewer tab was clicked.');
    $('#myDropdown').show(); // show the dropdown
    $('#myDropdown2').show();
});
//
// // listener on the Worlflow tab
// $('#workflow-tab').on('shown.bs.tab', function (e) {
//     console.log('Workflow tab was clicked.');
//     $('#myDropdown').hide(); // hide the dropdown
//     $('#dropdown-inefficiency').hide();
//
//     // hide the toolip raised by the section chart
//     d3.select('#tooltip').style('opacity', 0)
// });

function submitHelper(){
    menuSelection = [];
    var norm = document.ConfusionMatrixRadioButton.norm.value;
    var foldVal = document.cm_fold_level.button.value;
    var betaVal = document.cm_beta.button.value;
    var alphaVal = document.cm_alpha.button.value;
    var mode = document.getElementById("constrained").checked? "constrained": "unconstrained"
    var target_file = './dashboard/data/confusion_matrix/grid/' + mode
                        + '/alpha' + alphaVal + '_beta' + betaVal
                        + '/alpha' + alphaVal + '_beta' + betaVal + '_cm_raw_data.csv'

    menuSelection.norm = norm;
    menuSelection.mode = mode;
    menuSelection.foldVal = foldVal;
    menuSelection.alphaVal = alphaVal;
    menuSelection.betaVal = betaVal;
    menuSelection.target_file = target_file;
    return menuSelection
}