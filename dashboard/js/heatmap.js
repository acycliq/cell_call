function heatmap(dataset) {
    console.log("I am in heatmap.js")

    var svg = d3.select("#heat-chart").select("svg")

    var tsn = d3.transition().duration(1000);

    // var xLabels = d3.map(dataset, function (d) {return d.xLabel;}).keys(),
    //     yLabels = d3.map(dataset, function (d) {return d.yLabel;}).keys();

    var labels = {
        x: d3.map(dataset, function (d) {return d.xLabel;}).keys(),
        y: d3.map(dataset, function (d) {return d.yLabel;}).keys(),
    };

    var margin = {top: 10, right: 10, bottom: 130, left: 160};

    var width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom;

    // var dotSpacing = 0,
    //     dotWidth = width / (2 * (labels.x.length)),
    //     dotHeight = height / (2 * labels.y.length);

    var dot = {
        spacing: 0,
        width: width / (2 * (labels.x.length)),
        height: height / (2 * labels.y.length),
    }

    var valRange = d3.extent(dataset, function (d) {return d.val});

    // var colors = ['#2C7BB6', '#00A6CA', '#00CCBC', '#90EB9D', '#FFFF8C', '#F9D057', '#F29E2E', '#E76818', '#D7191C'];
    var bluecolors = ['#f7fbff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b'],
        redcolors  = ['#fff5f0','#fee0d2','#fcbba1','#fc9272','#fb6a4a','#ef3b2c','#cb181d','#a50f15','#67000d'];

    var colorScale = d3.scaleQuantile()
        .domain(valRange)
        .range(bluecolors);


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

    var xBand = d3.scaleBand().domain(labels.x).range([0, width]),
        yBand = d3.scaleBand().domain(labels.y).rangeRound([height-2*dot.height, 2*dot.height]);

    var axis = {
        x: d3.axisBottom(scale.x).ticks(labels.x.length).tickFormat((d, i) => labels.x[i]),
        y: d3.axisLeft(scale.y).ticks(labels.y.length).tickFormat((d, i) => labels.y[i]),
    };

    var zoom = d3.zoom()
        .scaleExtent([1, dot.height])
        .on("zoom", zoomed);

    var tooltip = d3.select("body").append("div")
        .attr("id", "tooltip")
        .style("opacity", 0);

    // SVG canvas
    svg = d3.select("#heat-chart").select("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        // .call(zoom)
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
        // .attr("transform", "translate(0," + scale.y(-0.5) + ")")

    //Create Y axis
    var renderYAxis = svg.append("g")
        .attr("class", "y axis")
        // .attr("transform", "translate(0," + (-1)*dot.height + ")")


    function zoomed() {
        d3.event.transform.y = 0;
        d3.event.transform.x = Math.min(d3.event.transform.x, 5);
        d3.event.transform.x = Math.max(d3.event.transform.x, (1 - d3.event.transform.k) * width);

        // update: rescale x axis
        renderXAxis.call(axis.x.scale(d3.event.transform.rescaleX(scale.x)));

        // Make sure that only the x axis is zoomed
        heatDotsGroup.attr("transform", d3.event.transform.toString().replace(/scale\((.*?)\)/, "scale($1, 1)"));
    }

    // text label for the x axis
    svg.append("text")
      .attr("transform",
            "translate(" + (width/2) + " ," +
                           (height + margin.bottom) + ")")
      .style("text-anchor", "middle")
      .text("Predicted");

    // text label for the y axis
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y",0 - margin.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Actual");

    var chartData = {};
    chartData.scale = scale;
    // chartData.xLabels = xLabels;
    // chartData.yLabels = yLabels;
    chartData.labels = labels;
    chartData.axis = axis;
    chartData.xBand = xBand;
    chartData.yBand = yBand;
    chartData.colorScale = colorScale;
    chartData.heatDotsGroup = heatDotsGroup;
    // chartData.dotWidth = dotWidth;
    // chartData.dotHeight = dotHeight;
    chartData.dot = dot;
    chartData.tsn = tsn;
    chartData.width = width;
    chartData.height = height;
    chartData.margin = margin;

    return chartData;

};

function updateScales(data, scale){
    scale.x.domain([0.5, 0.5+d3.max(data, d => d.xKey)]),
    scale.y.domain([0.5, 0.5+d3.max(data, d => d.yKey)])
}

function updateLabels(data, labels){
    labels.x = d3.map(data, function (d) {return d.xLabel;}).keys(),
    labels.y = d3.map(data, function (d) {return d.yLabel;}).keys()
}

function updateDot(dot, width, height, labels){
    dot.width = width / (2 * (labels.x.length)),
    dot.height = height / (2 * labels.y.length)
}

function updateAxes(data, scale, labels, axis){
    axis.x = d3.axisBottom(scale.x).ticks(labels.x.length).tickFormat((d, i) => labels.x[i]),
    axis.y = d3.axisLeft(scale.y).ticks(labels.y.length).tickFormat((d, i) => labels.y[i])
}


function renderHeatmap(dataset) {
    var percentFormat = d3.format('.2%');

    var svg = d3.select("#heat-chart")
        .select("svg");
    if (svg.select("#clip2").empty()) {
        chartData = heatmap(dataset);
    }

    //chartData = svg.datum();
    //Do the axes
    updateScales(dataset, chartData.scale);

    updateAxes(dataset, chartData.scale, chartData.labels, chartData.axis);

    updateLabels(dataset, chartData.labels);

    updateDot(chartData.dot, chartData.width, chartData.height, chartData.labels);

    svg.select('.y.axis').call(chartData.axis.y)
    svg.select('.x.axis')
        .attr("transform", "translate(0, " + chartData.height + ")")
        .call(chartData.axis.x)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-60)");


    // Do the chart
    const update = chartData.heatDotsGroup.selectAll("ellipse")
        .data(dataset);

    update
        .enter()
        .append("ellipse")
        .attr("rx", chartData.dot.width)
        .attr("ry", chartData.dot.height)
        .on("mouseover", function (d) {
            $("#tooltip").html("Predicted: " + d.xLabel + "<br/>Actual: " + d.yLabel + "<br/>Prob: " + percentFormat(d.val));
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
        .attr("cx", function (d) {return chartData.scale.x(d.xKey);})
        .attr("cy", function (d) {return chartData.scale.y(d.yKey);})
        .attr("fill", function (d) { return chartData.colorScale(d.val);} );

    update.exit().remove();

}
