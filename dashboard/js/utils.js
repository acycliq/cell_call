
function partitioner(d){

    // For small values assign it to a separate class labeled 'Other'
    var datapoint = [];
    var ClassName;
    if (!Array.isArray(d.Prob)){
        //d.Prob can possibly be just a float. Make sure it is an array
        d.Prob = [d.Prob]
    }
    for (var i = 0; i < d.Prob.length; i++) {
        d.Prob[i] < 0.02? ClassName = 'Other': ClassName = d.ClassName[i]
        datapoint.push({
            Prob: d.Prob[i],
            labels: ClassName,
        })
    }

    // group by class name. This will eventually sum all the values that fall in the same class.
    //Hence if there is a class 'Other' then is will be assigned with the grand total
    datapoint =  d3.nest().key(function(d){
        return d.labels; })
        .rollup(function(leaves){
            return d3.sum(leaves, function(d){
                return d.Prob;})
        }).entries(datapoint)
        .map(function(d){
            return { labels: d.key, Prob: d.value};
        });

    // sort in decreasing order
    datapoint.sort(function(x, y){
        return d3.ascending(y.Prob, x.Prob);
    })

    return datapoint;
}



function dispachClick(layer) {
    var evtxClick = new CustomEvent('clickMouse');
    var evtyClick = new CustomEvent('clickMouse');

    document.getElementById("xxValue").value = layer.feature.properties.cx,
        document.getElementById("yyValue").value = layer.feature.properties.cy,
        document.getElementById('xxValue').dispatchEvent(evtxClick),
        document.getElementById('yyValue').dispatchEvent(evtxClick)
    // I think there is a reason in the line above I used evtxClick and NOT evtyClick
    // Something with convenience but there is a potential bug here
    // Why did you do that?? Remember and fix!
}


function dispachCustomEvent(layer) {
    var evtxx = new CustomEvent('moveMouse');
    var evtyy = new CustomEvent('moveMouse');

    //Thats a temp solution to make the scatter chart responsive.
    document.getElementById("xxValue").value = layer.feature.properties.cx,
        document.getElementById("yyValue").value = layer.feature.properties.cy,
        document.getElementById('xxValue').dispatchEvent(evtxx),
        document.getElementById('yyValue').dispatchEvent(evtyy)

}


/**
 * Retrieve the array key corresponding to the largest element in the array.
 *
 * @param {Array.<number>} array Input array
 * @return {number} Index of array element with largest value
 *
 * From https://gist.github.com/engelen/fbce4476c9e68c52ff7e5c2da5c24a28
 */
function argMax(array) {
  return array.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
}

function diagonalMean(dataset){
    var arr = []
    xLabels = d3.map(dataset, function (d){return d.xLabel;}).keys();
    yLabels = d3.map(dataset, function (d){return d.yLabel;}).keys();

    // remove from x-axis those classes that do not appear in y axis
    data = dataset.filter(function(d){ return yLabels.includes(d.xLabel)});

    // take now all the elements in the diagonal
    diagonal_obj = data.filter(function(d){ return d.yLabel === d.xLabel});

    for (i=0; i< diagonal_obj.length; ++i){
       arr[i] = diagonal_obj[i].val
    }

    console.log('Array across the diagonal is: ' + arr)

    // arr = d3.map(diagonal_obj, function(d) {return d.val}).keys()
    //
    // // convert to float
    // arr = arr.map(function(d){ return +d;});

    //take the total sum
    sum = arr.reduce((a,b)=>a+b, 0)

    // calc the mean
    score = sum / arr.length

    console.log('Confusion matrix score: ' + score)

    out = []
    out.push({
        "metric": 'Diagonal Mean',
        "value": score,
    })
    return out

}


function convertArrayOfObjectsToCSV(args) {
    var result, ctr, keys, columnDelimiter, lineDelimiter, data;

    data = args.data || null;
    if (data == null || !data.length) {
        return null;
    }

    columnDelimiter = args.columnDelimiter || ',';
    lineDelimiter = args.lineDelimiter || '\n';

    keys = Object.keys(data[0]);

    result = '';
    result += keys.join(columnDelimiter);
    result += lineDelimiter;

    data.forEach(function (item) {
        ctr = 0;
        keys.forEach(function (key) {
            if (ctr > 0) result += columnDelimiter;

            result += item[key];
            ctr++;
        });
        result += lineDelimiter;
    });

    return result;
}

function saveCsv(args) {
    // from https://halistechnology.com/2015/05/28/use-javascript-to-export-your-data-as-csv/
    var data, filename, link;

    filename = menuSelection.norm + '_fold' + menuSelection.foldVal + '_alpha' + menuSelection.alphaVal + '_beta' + menuSelection.betaVal + '.csv'

    var csv = convertArrayOfObjectsToCSV({
        data: cm_dataset
    });
    if (csv == null) return;

    // filename = args.filename || 'export.csv';

    if (!csv.match(/^data:text\/csv/i)) {
        csv = 'data:text/csv;charset=utf-8,' + csv;
    }
    data = encodeURI(csv);

    link = document.createElement('a');
    link.setAttribute('href', data);
    link.setAttribute('download', filename);
    link.click();
}

function deleteCookie(keyName) {
    sessionStorage.removeItem('keyName')
}