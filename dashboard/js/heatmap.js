function heatmap(dataset) {
    console.log("I am in heatmap.js")

    var svg = d3.select("#heat-chart").select("svg")

    var tsn = d3.transition().duration(1000);

    var xLabels = d3.map(dataset, function (d) {return d.xLabel;}).keys(),
        yLabels = d3.map(dataset, function (d) {return d.yLabel;}).keys();

    var margin = {top: 0, right: 0, bottom: 20, left: 55};

    var width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom;

    var dotSpacing = 0,
        dotWidth = width / (2 * (xLabels.length)),
        dotHeight = height / (2 * yLabels.length);

    var valRange = d3.extent(dataset, function (d) {return d.val});

    var colors = ['#2C7BB6', '#00A6CA', '#00CCBC', '#90EB9D', '#FFFF8C', '#F9D057', '#F29E2E', '#E76818', '#D7191C'];

    var colorScale = d3.scaleQuantile()
        .domain([valRange[0], colors.length - 1, valRange[1]])
        .range(colors);


    var max_val = d3.max( dataset, function(d) { return d.val });
    var min_val = d3.min( dataset, function(d) { return d.val });
    var median_val = d3.median( dataset, function(d) { return d.val });
    var color_scale = d3.scaleLinear().domain([min_val, median_val, max_val]).range(['blue', 'beige', 'red']);

    // the scale
    var scale = {
        x: d3.scaleLinear().range([0, width]),
        y: d3.scaleLinear().range([height, 0]),
    };

    var q = {
        x: d3.scaleQuantile().range([0, width])
    };

    var xBand = d3.scaleBand().domain(xLabels).range([0, width]),
        yBand = d3.scaleBand().domain(yLabels).rangeRound([height-2*dotHeight, 2*dotHeight]);

    var axis = {
        x: d3.axisBottom(scale.x).tickFormat((d, e) => xLabels[d]),
        y: d3.axisLeft(scale.y).ticks(yLabels.length).tickFormat((d, e) => yLabels[d]),
    };

    var zoom = d3.zoom()
        .scaleExtent([1, dotHeight])
        .on("zoom", zoomed);

    var tooltip = d3.select("body").append("div")
        .attr("id", "tooltip")
        .style("opacity", 0);

    // SVG canvas
    svg = d3.select("#heat-chart").select("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .call(zoom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Clip path
    svg.append("clipPath")
        .attr("id", "clip2")
        .append("rect")
        .attr("width", width)
        .attr("height", height);


    // Heatmap dots
    var heatDotsGroup = svg.append("g")
        .attr("clip-path", "url(#clip2)")
        .append("g");


    //Create X axis
    var renderXAxis = svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + scale.y(-0.5) + ")")

    //Create Y axis
    var renderYAxis = svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0," + (-1)*dotHeight + ")")


    function zoomed() {
        d3.event.transform.y = 0;
        d3.event.transform.x = Math.min(d3.event.transform.x, 5);
        d3.event.transform.x = Math.max(d3.event.transform.x, (1 - d3.event.transform.k) * width);

        // update: rescale x axis
        renderXAxis.call(axis.x.scale(d3.event.transform.rescaleX(scale.x)));

        // Make sure that only the x axis is zoomed
        heatDotsGroup.attr("transform", d3.event.transform.toString().replace(/scale\((.*?)\)/, "scale($1, 1)"));
    }

    var chartData = {};
    chartData.scale = scale;
    chartData.axis = axis;
    chartData.xBand = xBand;
    chartData.yBand = yBand;
    chartData.colorScale = colorScale;
    chartData.heatDotsGroup = heatDotsGroup;
    chartData.dotWidth = dotWidth;
    chartData.dotHeight = dotHeight;
    chartData.tsn = tsn;

    return chartData;

};

function updateScales(data, scale){
    scale.x.domain([0, d3.max(data, d => d.xKey)]),
    scale.y.domain([0, d3.max(data, d => d.yKey)])
}

function renderHeatmap(dataset) {

    var svg = d3.select("#heat-chart")
        .select("svg");
    if (svg.select("#clip").empty()) {
        chartData = heatmap(dataset);
    }

    //chartData = svg.datum();
    //Do the axes
    updateScales(dataset, chartData.scale);
    svg.select('.y.axis').call(chartData.axis.y)
    svg.select('.x.axis')
        .attr("transform", "translate(0, " + chartData.scale.y(0.0) + ")")
        .call(chartData.axis.x)


    // Do the chart
    const update = chartData.heatDotsGroup.selectAll("ellipse")
        .data(dataset);

    update
        .enter()
        .append("ellipse")
        .attr("rx", chartData.dotWidth)
        .attr("ry", chartData.dotHeight)
        .on("mouseover", function (d) {
            $("#tooltip").html("x: " + d.xLabel + "<br/>y: " + d.yLabel + "<br/>Value: " + Math.round(d.val * 100) / 100);
            var xpos = d3.event.pageX + 10;
            var ypos = d3.event.pageY + 20;
            $("#tooltip").css("left", xpos + "px").css("top", ypos + "px").animate().css("opacity", 1);
        }).on("mouseout", function () {
            $("#tooltip").animate({
                duration: 500
            }).css("opacity", 0);
        })
        .merge(update)
        .transition(chartData.tsn)
        .attr("cx", function (d) {return chartData.scale.x(d.xKey) - chartData.xBand.bandwidth();})
        .attr("cy", function (d) {return chartData.scale.y(d.yKey) + chartData.yBand.bandwidth();})
        .attr("fill", function (d) { return chartData.colorScale(d.val*25);} );

    update.exit().remove();

}
