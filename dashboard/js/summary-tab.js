

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

        var mydata = data.filter(function(item){
            for (var key in filter){
                if (item[key]===undefined || item[key] != filter[key])
                    return false
            }
            return true
        });
        console.log(mydata);
        var myChartObj = [];
        var chartObj1 = [];
        chartObj1.data = [];
        chartObj1.divId = '#summary-tab-chart-1';
        chartObj1.clipId = '#clipSubHeatMap';
        renderSubHeatmap(mydata, '#summary-tab-chart-1', myChartObj);

        // cm_dataset = heatmapDataManager(data, menuSelection.norm, +menuSelection.foldVal);
        // console.log('data from '+ menuSelection.target_file + ' fed into the confusion matrix');
        // renderHeatmap(cm_dataset);
        // var diagonalScore = diagonalMean(cm_dataset);
        // cmAnalytics(diagonalScore)
        console.log('Done')
    })
}
