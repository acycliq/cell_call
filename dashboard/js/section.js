function section() {

    var totalWidth = 700,
        totalHeight = 275;

    var margin = {
        top: 10,
        left: 50,
        bottom: 30,
        right: 0
    }

    var width = totalWidth - margin.left - margin.right,
        height = totalHeight - margin.top - margin.bottom;

    var tsn = d3.transition().duration(200);

    // radius of points in the scatterplot
    var pointRadius = 2;

    var scale = {
        x: d3.scaleLinear().range([0, width]),
        y: d3.scaleLinear().range([height, 0]),
    };

    var axis = {
        x: d3.axisBottom(scale.x).ticks(xTicks).tickSizeOuter(0),
        y: d3.axisLeft(scale.y).ticks(yTicks).tickSizeOuter(0),
    };

    var gridlines = {
        x: d3.axisBottom(scale.x).tickFormat("").tickSize(height),
        y: d3.axisLeft(scale.y).tickFormat("").tickSize(-width),
    }

    // var colorScale = d3.scaleLinear().domain([0, 1]).range(['tomato', 'tomato']);
    var colorRamp = classColorsCodes()
    var colorMap = d3.map(colorRamp, function (d) {
        return d.className;
    });

    // select the root container where the chart will be added
    var container = d3.select('#scatter-plot');

    var zoom = d3.zoom()
        .scaleExtent([1, 20])
        //.on("zoom", zoomed);

    var tooltip = d3.select("body").append("div")
        .attr("id", "tooltip")
        .style("opacity", 0);

    // initialize main SVG
    var svg = container.select('svg')
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .call(zoom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Clip path
    svg.append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    //Create X axis
    var renderXAxis = svg.append("g")
        .attr("class", "x axis")

    //Create Y axis
    var renderYAxis = svg.append("g")
        .attr("class", "y axis")

    //Create X grilines
    var renderXGridline = svg.append("g")
        .attr("class", "x gridline")

    //Create Y gridlines
    var renderYGridline = svg.append("g")
        .attr("class", "y gridline")

    // set up axis generating functions
    var xTicks = Math.round(width / 50);
    var yTicks = Math.round(height / 50);


    var moveX = document.getElementById("xxValue");
    var moveY = document.getElementById("yyValue");


    function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
    }

    function renderOrder(y) {
        return y === 'Zero' ? 1 :
            y === 'PC' ? 2 :
                y === 'Non Neuron' ? 3 :
                    y === 'PC Other2' ? 4 :
                        y === 'PC Other1' ? 5 :
                            y === 'Bistratified' ? 6 :
                                y === 'Sst/Reln/NPY' ? 7 :
                                    y === 'IS1' ? 8 :
                                        y === 'CGE NGF' ? 9 :
                                            y === 'Basket' ? 10 :
                                                y === 'IS3' ? 11 :
                                                    y === 'Radiatum retrohip' ? 12 :
                                                        y === 'MGE NGF' ? 13 :
                                                            y === 'O/LM' ? 14 :
                                                                y === 'NGF/I-S transition' ? 15 :
                                                                    y === 'Trilaminar' ? 16 :
                                                                        y === 'Axo-axonic' ? 17 :
                                                                            y === 'O-Bi' ? 18 :
                                                                                y === 'Ivy' ? 19 :
                                                                                    y === 'Hippocamposeptal' ? 20 :
                                                                                        y === 'Cck Cxcl14+' ? 21 :
                                                                                            y === 'Cck Vip Cxcl14-' ? 22 :
                                                                                                y === 'Cck Cxcl14-' ? 23 :
                                                                                                    y === 'Unidentified' ? 24 :
                                                                                                        y === 'Cck Vip Cxcl14+' ? 25 :
                                                                                                            y === 'Cck Calb1/Slc17a8*' ? 26 :
                                                                                                                y === 'Backprojection' ? 27 :
                                                                                                                    y === 'IS2' ? 28 :
                                                                                                                        29;
    }


    var chartData = {};
    chartData.svg = svg;
    chartData.width = width;
    chartData.height = height;
    chartData.renderXAxis = renderXAxis;
    chartData.renderYAxis = renderYAxis;
    chartData.renderXGridline = renderXGridline;
    chartData.renderYGridline = renderYGridline;
    chartData.renderOrder = renderOrder;
    chartData.tsn = tsn;
    chartData.pointRadius = pointRadius;
    chartData.scale = scale;
    chartData.axis = axis;
    chartData.gridlines = gridlines;
    chartData.colorRamp = colorRamp;
    chartData.colorMap = colorMap;
    chartData.zoom = zoom;
    chartData.tooltip = tooltip;

    return chartData
}

function aggregator(data) {
    var out;
    out = d3.nest()
        .key(function (d) {
            return d.IdentifiedType;
        }) //group by IdentifiedType
        .rollup(function (leaves) {
            return {
                Prob: d3.sum(leaves, function (d) {
                    return d.Prob;
                }), //sum all the values with the same IdentifiedType
                color: leaves[0].color //Get the first color code. All codes with the same IdentifiedType are the same anyway
            }
        }).entries(data)
        .map(function (d) {
            return {IdentifiedType: d.key, Prob: d.value.Prob, color: d.value.color};
        });

    // sort in decreasing order
    out.sort(function (x, y) {
        return d3.ascending(y.Prob, x.Prob);
    })

    return out
}

function dataManager(sectionFeatures, data) {
    var chartData = [];
    for (var i = 0; i < data.length; ++i) {
        var temp = [];
        for (var j = 0; j < data[i].ClassName.length; ++j) {
            // console.log(data[i].ClassName[j])
            temp.push({
                IdentifiedType: sectionFeatures.colorMap.get(data[i].ClassName[j]).IdentifiedType,
                color: sectionFeatures.colorMap.get(data[i].ClassName[j]).color,
                Prob: data[i].Prob[j]? data[i].Prob[j]: [data[i].Prob] //Maybe that one is better
            })
        }
        var agg = aggregator(temp);
        chartData.push({
            x: data[i].x,
            y: data[i].y,
            GeneCountTotal: data[i].CellGeneCount.reduce((a, b) => a + b, 0), //get the sum of all the elements in the array
            IdentifiedType: agg[0].IdentifiedType,
            color: agg[0].color,
            Prob: agg[0].Prob,
            renderOrder: sectionFeatures.renderOrder(agg[0].IdentifiedType),

        })
    }

    return chartData
}

function sectionChart(data) {

    console.log('Doing Section Overview plot')

    var svg = d3.select('#scatter-plot').select("svg")
    if (svg.select('.dotOnScatter').empty()) {
        var sectionFeatures = section()
    }

    svg = sectionFeatures.svg;

    var managedData = dataManager(sectionFeatures, data)

    //update now data with a managedData property
    for (var i = 0; i < data.length; ++i) {
        data[i].managedData = managedData[i]
    }

    // sort in ascending order
    data.sort(function (x, y) {
        return d3.ascending(x.managedData.renderOrder, y.managedData.renderOrder);
    })

    var extent = {
        x: d3.extent(data, function (d) {
            return d.x
        }),
        y: d3.extent(data, function (d) {
            return d.y
        }),
    };

    function updateScales(data) {
        sectionFeatures.scale.x.domain([extent.x[0] * 0.99, extent.x[1] * 1.01]).nice()
        sectionFeatures.scale.y.domain([extent.y[0] * 0.99, extent.y[1] * 1.01]).nice()
    }

    updateScales(data);

    svg.select('.y.axis')
        .attr("transform", "translate(" + sectionFeatures.pointRadius + " 0)")
        .call(sectionFeatures.axis.y);

    var h = sectionFeatures.height + sectionFeatures.pointRadius;
    svg.select('.x.axis')
        .attr("transform", "translate(0, " + h + ")")
        .call(sectionFeatures.axis.x);

    var xGrid = svg.append("g")
        .attr("class", "grid")
        .call(sectionFeatures.gridlines.x);

    var yGrid = svg.append("g")
        .attr("class", "grid")
        .call(sectionFeatures.gridlines.y);

    var dotsGroup = svg.append("g")
        .attr("clip-path", "url(#clip)")
        .attr("transform", "translate(4, 0)") // no idea why!
        .append("g");

    //Do the chart
    var update = dotsGroup.selectAll("circle").data(data)

    update
        .enter()
        .append('circle')
        .attr('class', 'dotOnScatter')
        .attr('id', d => 'Cell_Num_' + d.Cell_Num)
        .attr('r', d => Math.sqrt(d.managedData.GeneCountTotal))
        .attr('cx', d => sectionFeatures.scale.x(d.x))
        .attr('cy', d => sectionFeatures.scale.y(d.y))
        .attr('fill', d => d.managedData.color)
        .attr('fill-opacity', 0.85)


    voronoiDiagram = d3.voronoi()
        .x(d => sectionFeatures.scale.x(d.x))
        .y(d => sectionFeatures.scale.y(d.y))
        .size([sectionFeatures.width, sectionFeatures.height])(data);

    // add a circle for indicating the highlighted point
    dotsGroup.append('circle')
        .attr('class', 'highlight-circle')
        .attr('r', sectionFeatures.pointRadius * 2) // increase the size if highlighted
        //.style('fill', '#FFCE00')
        .style('display', 'none');

    // add a rect for indicating the highlighted point when you mouseover on the dapi chart
    dotsGroup.append('rect')
        .attr('class', 'highlight-rect')


    // add the overlay on top of everything to take the mouse events
    dotsGroup.append('rect')
        .attr('class', 'overlay')
        .attr('id', 'sectionOverlay')
        .attr('width', sectionFeatures.width)
        .attr('height', sectionFeatures.height)
        // .style('fill', '#FFCE00')
        .style('opacity', 0)
        .on('click', mouseClickHandler)
        .on('mousemove', mouseMoveHandler)
        .on('mouseleave', () => {
            // hide the highlight circle when the mouse leaves the chart
            console.log('mouse leave');
            dapiConfig.map.removeLayer(voronoiMarker);
            highlight(null);
        });

    // Manually dispach a mouse click event. That will kick-off rendering of the other charts on the dashboard.
    // d3.select('.overlay').dispatch('click')


    //collect the coordinates of the circles and push the to the data object
    var nodes = d3.selectAll('circle').nodes();
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].getAttribute('class') === 'dotOnScatter') {
            data[i].cx = +nodes[i].getAttribute('cx')
            data[i].cy = +nodes[i].getAttribute('cy')
        }
    }

    sectionFeatures.zoom.on("zoom", zoomed);

    function zoomed() {
        d3.event.transform.x = d3.event.transform.x;
        d3.event.transform.y = d3.event.transform.y;

        // update: rescale x and y axes
        sectionFeatures.renderXAxis.call(sectionFeatures.axis.x.scale(d3.event.transform.rescaleX(sectionFeatures.scale.x)));
        sectionFeatures.renderYAxis.call(sectionFeatures.axis.y.scale(d3.event.transform.rescaleY(sectionFeatures.scale.y)));

        xGrid.call(sectionFeatures.gridlines.x.scale(d3.event.transform.rescaleX(sectionFeatures.scale.x)));
        yGrid.call(sectionFeatures.gridlines.y.scale(d3.event.transform.rescaleY(sectionFeatures.scale.y)));

        dotsGroup.attr("transform", d3.event.transform);
        // xGrid.attr("transform", d3.event.transform);
        // yGrid.attr("transform", d3.event.transform);
    }

// callback for when the mouse moves across the overlay
    function mouseMoveHandler() {
        // make sure you hide the rect
        d3.select('.highlight-rect')
            .attr("width", 0)
            .attr("height",0)
            .attr('opacity', 0)

        // get the current mouse position
        const [mx, my] = d3.mouse(this);

        // use the new diagram.find() function to find the voronoi site closest to
        // the mouse, limited by max distance defined by voronoiRadius
        //const site = voronoiDiagram.find(mx, my, voronoiRadius);
        const site = voronoiDiagram.find(mx, my);

        // highlight the point if we found one, otherwise hide the highlight circle
        highlight(site && site.data);

        highlightDapi(site && site.data)

    }

    function highlightDapi(d){

        try {
            dapiConfig.map.removeLayer(voronoiMarker)
        }
        catch(err) {
            // do nothing
        }

        if(d){
            styleVoronoiMarkers(d)
        }
    }

    var styleVoronoiMarkers = function (d) {
        var p = dapiConfig.t.transform(L.point([d.x, d.y]));
        voronoiMarker = L.circleMarker([p.y, p.x], {
            radius: 15,
            fillColor: "orange",
            color: "red",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.5,
            interactive: false,
        }).addTo(dapiConfig.map);
    }

// callback for when the mouse moves across the overlay
    function mouseClickHandler() {
        console.log('pageX is: ' + d3.event.pageX)
        console.log('pageY is: ' + d3.event.pageY)

        // get the current mouse position
        const [mx, my] = d3.mouse(this);

        // use the new diagram.find() function to find the voronoi site closest to
        // the mouse, limited by max distance defined by voronoiRadius
        //const site = voronoiDiagram.find(mx, my, voronoiRadius);
        const site = voronoiDiagram.find(mx, my);

        // 1. highlight the point if we found one, otherwise hide the highlight circle
        highlight(site && site.data);

        // 2.
        updateDashboard(site && site.data)

        // 3.
        drawMarker(site && site.data)

    }

    function drawMarker(d){
        if (dapiConfig){
            var p = dapiConfig.t.transform(L.point([d.x, d.y]));

            try {
                dapiConfig.map.removeLayer(voronoiMarker)
            }
            catch(err) {
                // do nothing
            }

            voronoiMarker = L.circleMarker([p.y, p.x], {
                radius: 15,
                fillColor: "orange",
                color: "red",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.5,
                interactive: false,
            }).addTo(dapiConfig.map);
        }
    }

    var prevHighlightDotNum = null;

// callback to highlight a point
    function highlight(d) {
        // no point to highlight - hide the circle and clear the text
        if (!d) {
            d3.select('.highlight-circle').style('display', 'none');
            prevHighlightDotNum = null;
            sectionFeatures.tooltip.style("opacity", 0);
            // otherwise, show the highlight circle at the correct position
        } else {
            if (prevHighlightDotNum !== d.Cell_Num) {
                d3.select('.highlight-circle')
                    .style('display', '')
                    .style('stroke', 'tomato')
                    .attr('fill', d.managedData.color)
                    .attr('cx', sectionFeatures.scale.x(d.x))
                    .attr('cy', sectionFeatures.scale.y(d.y))
                    .attr("r", 1.2 * Math.sqrt(d.managedData.GeneCountTotal));

                // If event has be triggered from the scatter chart, so a tooltip
                if (d3.event && d3.event.pageX) {

                    var myHtml = '<h4 style="margin-top:0px; margin-bottom:1px"><b>' + d.managedData.IdentifiedType + '</b></h4>' +
                        '<table style="width:95px;">' +
                        '<tbody>' +
                        '<tr style="width:95px; border-top:1px solid White; font-weight: bold">' +
                        '<td><div>Probability: </div></td>' +
                        '<td><div>' + Math.round(100 * d.managedData.Prob) / 100 + '</div></td>' +
                        '</tr>' +
                        '<tr class="">' +
                        '<td><div>Gene Count:</div>' + '</td>' +
                        '<td><div>' + Math.round(100 * d.managedData.GeneCountTotal) / 100 + '</div></td>' +
                        '</tr>' +
                        '</tbody>' +
                        '</table>'

                    sectionFeatures.tooltip.transition()
                        .duration(200)

                    sectionFeatures.tooltip
                        .style("opacity", .9)
                        .html(myHtml)
                        .style("left", (d3.event.pageX - 5) + "px")
                        .style("top", (d3.event.pageY + 25) + "px");

                }
                prevHighlightDotNum = d.Cell_Num;
            }
        }
    }


    // use that to check counts per IdentifiedType and then set the renderOrder in such a manner that
    // names which smaller counts (ie rarer) will be rendered on top of more frequent ones
    var countData = d3.nest()
        .key(function (d) {
            return d.managedData.IdentifiedType
        })
        .rollup(function (leaves) {
            return leaves.length
        })
        .entries(data)

    console.log('Finished Section Overview plot')
    return data
}

