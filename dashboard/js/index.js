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
        if (menuSelection.useBinaryClasses){
            data = use_binary_classes(data)
        };
        cm_dataset = heatmapDataManager(data, menuSelection.norm, +menuSelection.foldVal, +menuSelection.unfoldVal);
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


function heatmapDataManager(data, norm, dul, ddl) {
// Helper function to handle the data to be fed in to heatmap
// dul is the drill down level. Data are aggregated over that level.
// For example 'Astro.1', 'Astro.2' ,..., 'Astro.5' will all be combined
// in a big class 'Astro' if dul=1
// norm is either 'avg' or 'median'. The default is 'median'

    function stripper(d, k) {
        for (i = 0; i < k; ++i) {
            if (d.lastIndexOf('.') > 0) {
                d = d.substring(0, d.lastIndexOf('.'))
            }
        }
        return d
    }

    // find the position of the i-th occurrence of substring m in string str
    function getPosition(str, m, i) { return str.split(m, i).join(m).length; }

    // unstripper('this.is.a.test', 2) = 'this.is'
    // unstripper('this.is.a.test', 3) = 'this.is.a'
    function unstripper(d, k) {
        var out = d.substring(0, getPosition(d, '.', k+1));
        return out
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


    if ($('#layers-base-7 input:radio:checked').length){
        // var ddl = 4; //drill down level
        var result = data.map(o => Object.entries(o).reduce((o, [k, v]) => {
            //const firsts = k => k.split('.').slice(0, -1).join('.');
            if (k === 'model_class') {
                o[k] = unstripper(v, ddl);
            } else {
                k = unstripper(k, ddl);
                o[k] = (o[k] || 0) + parseFloat(v);
            }
            return o;
        }, {}));
    }


    if ($('#layers-base-6 input:radio:checked').length) {

        // var dul = 3; //drill down level
        var result = data.map(o => Object.entries(o).reduce((o, [k, v]) => {
            //const firsts = k => k.split('.').slice(0, -1).join('.');
            if (k === 'model_class') {
                o[k] = stripper(v, dul);
            } else {
                k = stripper(k, dul);
                o[k] = (o[k] || 0) + parseFloat(v);
            }
            return o;
        }, {}));
    }


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

$('#layers-base-8 input').change(function () {
    console.log('Binary Class checkbox changed status')
    $("#fold_row2").toggle($(this).is(":checked"))
    $("#unfold_row2").toggle($(this).is(":checked"))
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
    ["unfold_0", "unfold_1", "unfold_2", "unfold_3", "unfold_4", "unfold_5", "unfold_6", "unfold_7"].forEach(function (id) {
                document.getElementById(id).checked = false;
            });

    var target = submitHelper();
    renderHeatmapTab(target)
});

$('#layers-base-7 input').change(function () {
    ["fold_0", "fold_1", "fold_2", "fold_3", "fold_4", "fold_5", "fold_6", "fold_7"].forEach(function (id) {
                document.getElementById(id).checked = false;
            });

    var target = submitHelper();
    renderHeatmapTab(target)
});



// listener on the Confusion matrix tab
$('#confusion-table-tab').on('shown.bs.tab', function (e) {
    console.log('Confusion matrix tab was clicked.');
    // hide the navbar dropdown menus
    $('#myDropdown').hide();
    $('#myDropdown2').hide();
    $('#myDropdown3').hide();
    $('#myDropdown4').hide();
    $('#myDropdown5').hide();
    $("#fold_row2").hide();
    $("#unfold_row2").hide();
    var target = submitHelper();
    renderHeatmapTab(target)
});

// listener on the Viewer tab
$('#map-tab').on('shown.bs.tab', function (e) {
    console.log('Viewer tab was clicked.');
    $('#myDropdown').show(); // show the dropdown
    $('#myDropdown2').show();
    $('#myDropdown3').show();
    $('#myDropdown4').show();
    $('#myDropdown5').show();
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
    var unfoldVal = document.cm_unfold_level.button.value;
    var betaVal = document.cm_beta.button.value;
    var alphaVal = document.cm_alpha.button.value;
    var mode = document.getElementById("constrained").checked? "constrained": "unconstrained"
    var useBinaryClasses = document.getElementById("binaryClasses").checked? true: false;
    var target_file = './dashboard/data/confusion_matrix/grid/' + mode
                        + '/alpha' + alphaVal + '_beta' + betaVal
                        + '/alpha' + alphaVal + '_beta' + betaVal + '_cm_raw_data.csv'

    menuSelection.norm = norm;
    menuSelection.mode = mode;
    menuSelection.useBinaryClasses = useBinaryClasses;
    menuSelection.foldVal = foldVal;     //drilling up
    menuSelection.unfoldVal = unfoldVal; //drilling down
    menuSelection.alphaVal = alphaVal;
    menuSelection.betaVal = betaVal;
    menuSelection.target_file = target_file;
    return menuSelection
}


function use_binary_classes(data) {

    res = []
    data.forEach(function (d) {
        if (d.model_class === 'Sst.Nos1') {
            d.model_class = 'Sst.Sst.Pcp4'
        }
        if (d.model_class === 'Sst.Npy.Cort') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Npy.Cort'
        }
        if (d.model_class === 'Sst.Npy.Zbtb20') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Npy.Cdh13.Pcp4'
        }
        if (d.model_class === 'Sst.Npy.Serpine2') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Npy.Cdh13.Crhbp'
        }
        if (d.model_class === 'Sst.Npy.Mgat4c') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Npy'
        }
        if (d.model_class === 'Sst.Pnoc.Calb1.Igfbp5') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Pnoc.Nrsn1'
        }
        if (d.model_class === 'Sst.Pnoc.Calb1.Pvalb') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Pnoc.Cdh13'
        }
        if (d.model_class === 'Sst.Pnoc.Pvalb') {
            d.model_class = 'Sst.Sst.Rbp4.Rbp4.Rbp4.Col25a1'
        }
        if (d.model_class === 'Sst.Erbb4.Rgs10') {
            d.model_class = 'Sst.Sst.Rbp4.Rgs10'
        }
        if (d.model_class === 'Sst.Erbb4.Crh') {
            d.model_class = 'Sst.Pvalb.Rbp4.6330403K07Rik.Sst'
        }
        if (d.model_class === 'Sst.Erbb4.Th') {
            d.model_class = 'Sst.Pvalb.Rbp4.6330403K07Rik.Tac1.Sst'
        }
        if (d.model_class === 'Pvalb.Tac1.Nr4a2') {
            d.model_class = 'Sst.Pvalb.Rbp4.6330403K07Rik.Tac1.Pvalb'
        }
        if (d.model_class === 'Pvalb.Tac1.Sst') {
            d.model_class = 'Sst.Pvalb.Rbp4.Pvalb.Sst'
        }
        if (d.model_class === 'Pvalb.Tac1.Syt2') {
            d.model_class = 'Sst.Pvalb.Rbp4.Pvalb.Pvalb.Rbp4'
        }
        if (d.model_class === 'Pvalb.Tac1.Akr1c18') {
            d.model_class = 'Sst.Pvalb.Rbp4.Pvalb.Pvalb.Nsg2'
        }
        if (d.model_class === 'Pvalb.C1ql1.Pvalb') {
            d.model_class = 'Sst.Pvalb.Snca.Pvalb.Pvalb'
        }
        if (d.model_class === 'Pvalb.C1ql1.Cpne5') {
            d.model_class = 'Sst.Pvalb.Snca.Pvalb.Snca'
        }
        if (d.model_class === 'Pvalb.C1ql1.Npy') {
            d.model_class = 'Sst.Pvalb.Snca.Npy'
        }
        if (d.model_class === 'Cacna2d1.Lhx6.Reln') {
            d.model_class = 'Vip.Npy.Cryab.Npy.Nrsn1.Cox6a2'
        }
        if (d.model_class === 'Cacna2d1.Lhx6.Vwa5a') {
            d.model_class = 'Vip.Npy.Cryab.Npy.Nrsn1.Npy'
        }
        if (d.model_class === 'Cacna2d1.Ndnf.Npy') {
            d.model_class = 'Vip.Npy.Cryab.Npy.Kit.Npy'
        }
        if (d.model_class === 'Cacna2d1.Ndnf.Rgs10') {
            d.model_class = 'Vip.Npy.Cryab.Npy.Kit.Cnr1'
        }
        if (d.model_class === 'Cacna2d1.Ndnf.Cxcl14') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Cryab.Cxcl14.Npy'
        }
        if (d.model_class === 'Calb2.Cryab') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Cryab.Cxcl14.Calb2'
        }
        if (d.model_class === 'Sst.Cryab') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Cryab.Sst'
        }
        if (d.model_class === 'Ntng1.Synpr') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Ntng1.Cxcl14.Serpine2'
        }
        if (d.model_class === 'Ntng1.Rgs10') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Ntng1.Cxcl14.Nrip3'
        }
        if (d.model_class === 'Ntng1.Chrm2') {
            d.model_class = 'Vip.Npy.Cryab.Ntng1.Ntng1.Pcp4'
        }
        if (d.model_class === 'Cck.Sema5a') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Ntng1.Ntng1'
        }
        if (d.model_class === 'Cck.Lmo1.Npy') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Ntng1.Yjefn3.Trp53i11'
        }
        if (d.model_class === 'Cck.Calca') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Ntng1.Yjefn3.Cryab'
        }
        if (d.model_class === 'Cck.Lmo1.Vip.Fam19a2') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Vip.Krt73'
        }
        if (d.model_class === 'Cck.Lmo1.Vip.Crh') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Vip.Fxyd6.Vip'
        }
        if (d.model_class === 'Cck.Lmo1.Vip.Tac2') {
            d.model_class = 'Vip.Npy.Cnr1.Vip.Vip.Fxyd6.Npy'
        }
        if (d.model_class === 'Cck.Lypd1') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Lypd1'
        }
        if (d.model_class === 'Cck.Cxcl14.Calb1.Tnfaip8l3') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Vsnl1.Vsnl1'
        }
        if (d.model_class === 'Cck.Cxcl14.Calb1.Igfbp5') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Vsnl1.Npy'
        }
        if (d.model_class === 'Cck.Cxcl14.Slc17a8') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Kctd12'
        }
        if (d.model_class === 'Cck.Cxcl14.Calb1.Kctd12') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Rgs12.Kctd12'
        }
        if (d.model_class === 'Cck.Cxcl14.Calb1.Tac2') {
            d.model_class = 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Rgs12.Tac2'
        }
        if (d.model_class === 'Cck.Cxcl14.Vip') {
            d.model_class = 'Vip.Vip.Cck.Cck.Sncg'
        }
        if (d.model_class === 'Vip.Crh.Pcp4') {
            d.model_class = 'Vip.Vip.Cck.Cck.Crh.Pcp4'
        }
        if (d.model_class === 'Vip.Crh.C1ql1') {
            d.model_class = 'Vip.Vip.Cck.Cck.Crh.Apoe'
        }
        if (d.model_class === 'Calb2.Vip.Gpd1') {
            d.model_class = 'Vip.Vip.Cck.Myl1.Cpne2.Camk2n1'
        }
        if (d.model_class === 'Calb2.Vip.Igfbp4') {
            d.model_class = 'Vip.Vip.Cck.Myl1.Cpne2.Tac2'
        }
        if (d.model_class === 'Calb2.Vip.Nos1') {
            d.model_class = 'Vip.Vip.Cck.Myl1.Alcam'
        }
        if (d.model_class === 'Calb2.Cntnap5a.Rspo3') {
            d.model_class = 'Vip.Vip.Nnat.Cxcl14'
        }
        if (d.model_class === 'Calb2.Cntnap5a.Vip') {
            d.model_class = 'Vip.Vip.Nnat.Vip.Vsnl1'
        }
        if (d.model_class === 'Calb2.Cntnap5a.Igfbp6') {
            d.model_class = 'Vip.Vip.Nnat.Vip.Ntng1'
        }

        res.push({
            model_class: d.model_class
        })
    });

    var replaceKeyInObjectArray = (a, r) => a.map(o =>
        Object.keys(o).map((key) => ({[r[key] || key]: o[key]})
        ).reduce((a, b) => Object.assign({}, a, b)));

    var replaceMap = { //"abc": "yyj" }

        'Sst.Nos1': 'Sst.Sst.Pcp4',
        'Sst.Npy.Cort': 'Sst.Sst.Rbp4.Rbp4.Npy.Cort',
        'Sst.Npy.Zbtb20': 'Sst.Sst.Rbp4.Rbp4.Npy.Cdh13.Pcp4',
        'Sst.Npy.Serpine2': 'Sst.Sst.Rbp4.Rbp4.Npy.Cdh13.Crhbp',
        'Sst.Npy.Mgat4c': 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Npy',
        'Sst.Pnoc.Calb1.Igfbp5': 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Pnoc.Nrsn1',
        'Sst.Pnoc.Calb1.Pvalb': 'Sst.Sst.Rbp4.Rbp4.Rbp4.Camk2n1.Pnoc.Cdh13',
        'Sst.Pnoc.Pvalb': 'Sst.Sst.Rbp4.Rbp4.Rbp4.Col25a1',
        'Sst.Erbb4.Rgs10': 'Sst.Sst.Rbp4.Rgs10',
        'Sst.Erbb4.Crh': 'Sst.Pvalb.Rbp4.6330403K07Rik.Sst',
        'Sst.Erbb4.Th': 'Sst.Pvalb.Rbp4.6330403K07Rik.Tac1.Sst',
        'Pvalb.Tac1.Nr4a2': 'Sst.Pvalb.Rbp4.6330403K07Rik.Tac1.Pvalb',
        'Pvalb.Tac1.Sst': 'Sst.Pvalb.Rbp4.Pvalb.Sst',
        'Pvalb.Tac1.Syt2': 'Sst.Pvalb.Rbp4.Pvalb.Pvalb.Rbp4',
        'Pvalb.Tac1.Akr1c18': 'Sst.Pvalb.Rbp4.Pvalb.Pvalb.Nsg2',
        'Pvalb.C1ql1.Pvalb': 'Sst.Pvalb.Snca.Pvalb.Pvalb',
        'Pvalb.C1ql1.Cpne5': 'Sst.Pvalb.Snca.Pvalb.Snca',
        'Pvalb.C1ql1.Npy': 'Sst.Pvalb.Snca.Npy',
        'Cacna2d1.Lhx6.Reln': 'Vip.Npy.Cryab.Npy.Nrsn1.Cox6a2',
        'Cacna2d1.Lhx6.Vwa5a': 'Vip.Npy.Cryab.Npy.Nrsn1.Npy',
        'Cacna2d1.Ndnf.Npy': 'Vip.Npy.Cryab.Npy.Kit.Npy',
        'Cacna2d1.Ndnf.Rgs10': 'Vip.Npy.Cryab.Npy.Kit.Cnr1',
        'Cacna2d1.Ndnf.Cxcl14': 'Vip.Npy.Cryab.Ntng1.Cryab.Cxcl14.Npy',
        'Calb2.Cryab': 'Vip.Npy.Cryab.Ntng1.Cryab.Cxcl14.Calb2',
        'Sst.Cryab': 'Vip.Npy.Cryab.Ntng1.Cryab.Sst',
        'Ntng1.Synpr': 'Vip.Npy.Cryab.Ntng1.Ntng1.Cxcl14.Serpine2',
        'Ntng1.Rgs10': 'Vip.Npy.Cryab.Ntng1.Ntng1.Cxcl14.Nrip3',
        'Ntng1.Chrm2': 'Vip.Npy.Cryab.Ntng1.Ntng1.Pcp4',
        'Cck.Sema5a': 'Vip.Npy.Cnr1.Vip.Ntng1.Ntng1',
        'Cck.Lmo1.Npy': 'Vip.Npy.Cnr1.Vip.Ntng1.Yjefn3.Trp53i11',
        'Cck.Calca': 'Vip.Npy.Cnr1.Vip.Ntng1.Yjefn3.Cryab',
        'Cck.Lmo1.Vip.Fam19a2': 'Vip.Npy.Cnr1.Vip.Vip.Krt73',
        'Cck.Lmo1.Vip.Crh': 'Vip.Npy.Cnr1.Vip.Vip.Fxyd6.Vip',
        'Cck.Lmo1.Vip.Tac2': 'Vip.Npy.Cnr1.Vip.Vip.Fxyd6.Npy',
        'Cck.Lypd1': 'Vip.Npy.Cnr1.Cxcl14.Lypd1',
        'Cck.Cxcl14.Calb1.Tnfaip8l3': 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Vsnl1.Vsnl1',
        'Cck.Cxcl14.Calb1.Igfbp5': 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Vsnl1.Npy',
        'Cck.Cxcl14.Slc17a8': 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Kctd12',
        'Cck.Cxcl14.Calb1.Kctd12': 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Rgs12.Kctd12',
        'Cck.Cxcl14.Calb1.Tac2': 'Vip.Npy.Cnr1.Cxcl14.Kctd12.Kctd12.Rgs12.Tac2',
        'Cck.Cxcl14.Vip': 'Vip.Vip.Cck.Cck.Sncg',
        'Vip.Crh.Pcp4': 'Vip.Vip.Cck.Cck.Crh.Pcp4',
        'Vip.Crh.C1ql1': 'Vip.Vip.Cck.Cck.Crh.Apoe',
        'Calb2.Vip.Gpd1': 'Vip.Vip.Cck.Myl1.Cpne2.Camk2n1',
        'Calb2.Vip.Igfbp4': 'Vip.Vip.Cck.Myl1.Cpne2.Tac2',
        'Calb2.Vip.Nos1': 'Vip.Vip.Cck.Myl1.Alcam',
        'Calb2.Cntnap5a.Rspo3': 'Vip.Vip.Nnat.Cxcl14',
        'Calb2.Cntnap5a.Vip': 'Vip.Vip.Nnat.Vip.Vsnl1',
        'Calb2.Cntnap5a.Igfbp6': 'Vip.Vip.Nnat.Vip.Ntng1',


    };

    out = replaceKeyInObjectArray(data, replaceMap);


    return out
}

