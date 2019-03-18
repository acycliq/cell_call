function spotPopup(dataset) {


    var width = 400;
    var height = 150;
    var margin = {left: 40, right: 15, top: 40, bottom: 40};
    var parse = d3.timeParse("%m");
    var format = d3.timeFormat("%b");

    var svg = d3.select("#bar-chart").select("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
    var g = svg.append("g")
        .attr("transform", "translate(" + [margin.left, margin.top] + ")");

    var y = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    var yAxis = d3.axisLeft()
        .ticks(4)
        .scale(y);
    g.append("g").call(yAxis);

    // var x = d3.scaleBand()
    //     .domain(d3.range(4))
    //     .range([0, width]);

    var x = d3.scaleBand()
        .domain(dataset.labels)
        .range([0, width])
        .padding(0.1);

    var xAxis = d3.axisBottom()
        .scale(x);

    g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .attr("text-anchor", "middle")
        // .attr("transform", "rotate(-90)translate(-12,-15)")

    var rects = g.selectAll("rect")
        .data(dataset.Prob)
        .enter()
        .append("rect")
        .attr("y", height)
        .attr("height", 0)
        .attr("width", x.bandwidth() - 2)
        .attr("x", function (d, i) {
            return x(i);
        })
        .attr("fill", "steelblue")
        .transition()
        .attr("height", function (d) {
            return height - y(d);
        })
        .attr("y", function (d) {
            return y(d);
        })
        .duration(1000);

    var title = svg.append("text")
        .style("font-size", "20px")
        .text('My title')
        .attr("x", width / 2 + margin.left)
        .attr("y", 30)
        .attr("text-anchor", "middle");

    // return div.node();

}