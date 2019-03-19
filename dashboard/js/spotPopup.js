function spotPopup(d) {
// From https://bl.ocks.org/d3noob/bdf28027e0ce70bd132edc64f1dd7ea4
// and http://bl.ocks.org/andrew-reid/11602fac1ea66c2a6d7f78067b2deddb

    var data = d.feature.properties.neighbours;


// set the dimensions and margins of the graph
    var width = 100;
    var height = 50;
    var margin = {left:40,right:15,top:20,bottom:40};

// set the ranges
    var x = d3.scaleBand().range([0, width]).padding(0.1);

    var xAxis = d3.axisBottom()
                .scale(x);

    var y = d3.scaleLinear().range([height, 0]);

    var yAxis = d3.axisLeft()
                .ticks(4)
                .scale(y);

// append the svg object to the body of the page
// append a 'group' element to 'svg'
// moves the 'group' element to the top left margin
    var div = d3.create("div");
    var svg = div.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    // Scale the range of the data in the domains
    x.domain(data.map(function (d) {
        return d.Cell_Num;
    }));
    y.domain([0, 1]);

    // append the rectangles for the bar chart
    svg.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("y",height)
        .attr("height",0)
        .attr("width", x.bandwidth())
        .attr("x", function (d) {return x(d.Cell_Num);})
        .attr("fill","steelblue")
        .transition()
        .attr("height", function (d) { return height - y(d.Prob); })
        .attr("y", function (d) {return y(d.Prob);})
        .duration(1000);


    // add the x Axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // add the y Axis
    svg.append("g")
        .call(yAxis);

    return div.node();

}