
// THESE ARE NOW IN THE GLOBAL SCOPE
var cookie = sessionStorage['myvariable'],
    cookie2 = sessionStorage['myvariable2'],
    cookie3 = sessionStorage['myvariable3'],
    cookie4 = sessionStorage['myvariable4'],
    cookie5 = sessionStorage['myvariable5'],
    cookie6 = sessionStorage['myvariable6'],
    cellData,
    geneData;


if ((!cookie) && (!cookie2) && (!cookie3) && (!cookie4) && (!cookie5)&& (!cookie6)  ){ // if you dont have cookie, run the default selection
    console.log('No cookie, starting with default dataset')
    var configSettings = config().get('98 gene panel')
}
else {
    if (cookie)
    {
        console.log('Found cookie: ' + cookie);
        var configSettings = config().get(cookie)
    }
    else if (cookie2)
    {
        console.log('Found cookie: ' + cookie2);
        var configSettings = config().get(cookie2)
    }
    else if (cookie3)
    {
        console.log('Found cookie: ' + cookie3);
        var configSettings = config().get(cookie3)
    }
    else if (cookie4)
    {
        console.log('Found cookie: ' + cookie4);
        var configSettings = config().get(cookie4)
    }
    else if (cookie5)
    {
        console.log('Found cookie: ' + cookie5);
        var configSettings = config().get(cookie5)
    }
    else
    {
        console.log('Found cookie: ' + cookie6);
        var configSettings = config().get(cookie6)
    }

}
run(configSettings)

// function inefficiencySelector(x){
//     // 1. Show the dropdown to select the inefficiency
//     $('#dropdown-inefficiency').show()
//
//     // 2.
//     d3.select('.myDropdown').node().text = x + '  ';
//     $('.myDropdown').append("<span class='caret'></span>");
//
// }

function dispatcher(x){
    console.log('you clicked '+ x)

    //save a cookie
    sessionStorage['myvariable'] = x;

    // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable2');
    sessionStorage.removeItem('myvariable3');
    sessionStorage.removeItem('myvariable4');
    sessionStorage.removeItem('myvariable5');
    sessionStorage.removeItem('myvariable6');

    //reload page
    location.reload(true);

}

function dispatcher2(x2){
    console.log('you clicked '+ x2)

    // save a cookie
    sessionStorage['myvariable2'] = x2;

    // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable');
    sessionStorage.removeItem('myvariable3');
    sessionStorage.removeItem('myvariable4');
    sessionStorage.removeItem('myvariable5');
    sessionStorage.removeItem('myvariable6');

    //reload page
    location.reload(true);

}

function dispatcher3(x3){
    console.log('you clicked '+ x3);

    // save a cookie
    sessionStorage['myvariable3'] = x3;

    // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable');
    sessionStorage.removeItem('myvariable2');
    sessionStorage.removeItem('myvariable4');
    sessionStorage.removeItem('myvariable5');
    sessionStorage.removeItem('myvariable6');

    //reload page
    location.reload(true);

}

function dispatcher4(x4){
    console.log('you clicked '+ x4)

    // save a cookie
    sessionStorage['myvariable4'] = x4;

   // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable');
    sessionStorage.removeItem('myvariable2');
    sessionStorage.removeItem('myvariable3');
    sessionStorage.removeItem('myvariable5')
    sessionStorage.removeItem('myvariable6');

    //reload page
    location.reload(true);

}

function dispatcher5(x5){
    console.log('you clicked '+ x5)

    // save a cookie
    sessionStorage['myvariable5'] = x5;

    // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable');
    sessionStorage.removeItem('myvariable2');
    sessionStorage.removeItem('myvariable3');
    sessionStorage.removeItem('myvariable4');
    sessionStorage.removeItem('myvariable6');

    //reload page
    location.reload(true);

}

function dispatcher6(x6){
    console.log('you clicked '+ x6)

    // save a cookie
    sessionStorage['myvariable6'] = x6;

    // delete the cookie from other dropdowns
    sessionStorage.removeItem('myvariable');
    sessionStorage.removeItem('myvariable2');
    sessionStorage.removeItem('myvariable3');
    sessionStorage.removeItem('myvariable4');
    sessionStorage.removeItem('myvariable5');

    //reload page
    location.reload(true);

}

// function set_inefficiency(x){
//     d3.select('.dropdown-inefficiency').node().text = 'Inefficiency: ' + x
//     $('.dropdown-inefficiency').append("<span class='caret'></span>");
//     $('.dropdown-inefficiency').dropdown('toggle')
// }

function run(c){
    var cellJson = c.cellData;
    var geneJson = c.geneData;

    if (configSettings.name === '98 gene panel'){
        d3.queue()
        .defer(d3.json, cellJson)
        .defer(d3.json, geneJson)
        .await(splitCharts(c))
    }
    else {
        d3.queue()
        .defer(d3.json, cellJson)
        .defer(d3.csv, geneJson)
        .await(splitCharts(c))
    }

}


function splitCharts(myParam) {
    return (err, ...args) => {

        cellData = args[0];
        geneData = args[1];

        for (i = 0; i < cellData.length; ++i) {
            // make sure Prob and ClassName are arrays
            cellData[i].myProb = Array.isArray(cellData[i].Prob)? cellData[i].Prob: [cellData[i].Prob];
            cellData[i].myClassName = Array.isArray(cellData[i].ClassName)? cellData[i].ClassName: [cellData[i].ClassName];

            cellData[i].Cell_Num = +cellData[i].Cell_Num;
            cellData[i].x = +cellData[i].X;
            cellData[i].y = +cellData[i].Y;
        }

        //render now the charts
        var issData = sectionChart(cellData);
        dapiChart(issData, geneData, myParam);
        landingPoint(configSettings.name)
    }
}

function landingPoint(name){
    var coords = getLandingCoords(name)

    var evt = new MouseEvent("click", {
        view: window,
        bubbles: true,
        cancelable: true,
        clientX: coords.x,
        clientY: coords.y,
        /* whatever properties you want to give it */
    });
    document.getElementById('sectionOverlay').dispatchEvent(evt);
}

//create ramp
function getLandingCellNum(str) {
    return str === '99 gene panel' ? 2279 :
        str === '98 gene panel' ? 2279 :
            str === 'Simulated spots (98 gene panel)' ? 2279 :
                str === 'Simulated spots (62 gene panel)' ? 2279 :
                    str === 'Simulated spots (42 gene panel)' ? 2279 :
                            2279;
}


function getLandingCoords(str){
    console.log('Getting the landing cell')
    var cn = getLandingCellNum(str);
    var x,
        y;

    if ( !d3.select('#Cell_Num_' + cn).empty() ){
        x = +d3.select('#Cell_Num_' + cn).attr('cx');
        y = +d3.select('#Cell_Num_' + cn).attr('cy');
    }
    else{
        x = 0;
        y = 0;
    }

    var px = $('#sectionOverlay').offset().left + x;
    var py = $('#sectionOverlay').offset().top + y;

    var out = {x:px, y:py};

    return out
}

function getMinZoom(str) {
    return str === 'default' ? 4 : 2;
}
