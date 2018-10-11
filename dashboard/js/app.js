

var cookie = sessionStorage['myvariable']

if (!cookie){ // if you dont have cookie, run the default selection
    console.log('No cookie, starting with default dataset')
    var configSettings = config().get('default')
}
else {
    console.log('Found cookie: ' + cookie)
    var configSettings = config().get(cookie)
}
run(configSettings)

function dispatcher(x){
    console.log('you clicked '+ x)

    //save a cookie
    sessionStorage['myvariable'] = x;

    //reload page
    location.reload(true);

}


function run(c){
    var cellJson = c.cellData;
    var geneJson = c.geneData;

    d3.queue()
        .defer(d3.json, cellJson)
        .defer(d3.csv, geneJson)
        .await(splitCharts(c))
}


function splitCharts(myParam) {
    return (err, ...args) => {

        var cellData = args[0];
        var geneData = args[1];

        for (i = 0; i < cellData.length; ++i) {
            cellData[i].Cell_Num = +cellData[i].Cell_Num
            cellData[i].x = +cellData[i].X
            cellData[i].y = +cellData[i].Y
        }

        //render now the charts
        var issData = sectionChart(cellData);
        dapiChart(issData, geneData, myParam)
    }
}
