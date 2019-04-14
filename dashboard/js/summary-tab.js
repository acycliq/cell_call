
chartObj = []; //global scope!!
chartObj2 = []; //global scope!!
chartObj3 = []; //global scope!!
chartObj4 = []; //global scope!!
// listener on the Worlflow tab
$('#workflow-tab').on('shown.bs.tab', function (e) {
    console.log('Workflow tab was clicked.');
    $('#myDropdown').hide(); // hide the dropdown
    $('#myDropdown2').hide(); // hide the dropdown

    // hide the toolip raised by the section chart
    d3.select('#tooltip').style('opacity', 0)

    renderSubHeatmapManager()
});


function renderSubHeatmapManager() {

    d3.csv("./notebooks/cm_summary.csv", function(data){
        data.forEach(function(d) {
            d.xKey = +d.xKey;
            d.yKey = +d.yKey;
            d.val = +d.val;
        });

        var filter = {mode:'constrained', norm:'mean', fold:0};
        chartObj.divId = '#summary-tab-chart-1';
        chartObj.clipId = 'clipSubHeatMap-1'; // WITHOUT THE # SYMBOL
        chartObj.clipHashId = '#clipSubHeatMap-1';
        subplot(data, filter, chartObj)

        var filter2 = {mode:'constrained', norm:'mean', fold:1};
        chartObj2.divId = '#summary-tab-chart-2';
        chartObj2.clipId = 'clipSubHeatMap-2'; // WITHOUT THE # SYMBOL
        chartObj2.clipHashId = '#clipSubHeatMap-2';
        subplot(data, filter2, chartObj2)

        var filter3 = {mode:'constrained', norm:'mean', fold:2};
        chartObj3.divId = '#summary-tab-chart-3';
        chartObj3.clipId = 'clipSubHeatMap-3'; // WITHOUT THE # SYMBOL
        chartObj3.clipHashId = '#clipSubHeatMap-3';
        subplot(data, filter3, chartObj3)

        var filter4 = {mode:'constrained', norm:'mean', fold:3};
        chartObj4.divId = '#summary-tab-chart-4';
        chartObj4.clipId = 'clipSubHeatMap-4'; // WITHOUT THE # SYMBOL
        chartObj4.clipHashId = '#clipSubHeatMap-4';
        subplot(data, filter4, chartObj4)


        // subplot('mean')

        // var mydata = data.filter(function(item){
        //     for (var key in filter){
        //         if (item[key]===undefined || item[key] != filter[key])
        //             return false
        //     }
        //     return true
        // });
        //
        // renderSubHeatmap(mydata, chartObj);
        // console.log('Done')
    })
}

// function subplot(arg){
//     var filter = {mode:'constrained', norm:arg, fold:0};
//     chartObj.divId = '#summary-tab-chart-1';
//     chartObj.clipId = 'clipSubHeatMap'; // WITHOUT THE # SYMBOL
//     chartObj.clipHashId = '#clipSubHeatMap';
//     subplotWorker(data, filter, chartObj)
// }

function subplot(data, filter, chartObj) {
    // var filter = {mode: 'constrained', norm: 'mean', fold: 0};

    var mydata = data.filter(function (item) {
        for (var key in filter) {
            if (item[key] === undefined || item[key] != filter[key])
                return false
        }
        return true
    });
    console.log(mydata);
    // chartObj.divId = '#summary-tab-chart-1';
    // chartObj.clipId = 'clipSubHeatMap'; // WITHOUT THE # SYMBOL
    // chartObj.clipHashId = '#clipSubHeatMap';
    renderSubHeatmap(mydata, chartObj);

}