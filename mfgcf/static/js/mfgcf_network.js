var width = 1000;
var height = 500;
var border = 1;
var bordercolor='black';

var svg = d3.select("#network").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("border", border);

var borderPath = svg.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("height", height)
    .attr("width", width)
    .style("stroke", bordercolor)
    .style("fill", "none")
    .style("stroke-width", border);

var color = d3.scaleOrdinal(d3.schemeCategory10);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody().strength(-30).distanceMax(150).distanceMin(10))
    // .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

var link = null;
var node = null;

// Stop the simulation and restart once the data has arrived
simulation.stop()
d3.json(url, function (error, graph) {

    if (error) throw error;

    svg.call(d3.zoom().on("zoom", redraw));

    function redraw() {
        svg.selectAll("circle").attr("transform", d3.event.transform).attr("translate", d3.event.translate);
        svg.selectAll("line").attr("transform", d3.event.transform).attr("translate", d3.event.translate);
    }

    link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", function (d) {
            if (d.validated) {
                return 0.4 * d.weight;
            }
            else
                return 0.2 * d.weight;
        })
        .attr("stroke", function (d) {
            if (d.validated) {
                return "red";
            } else {
                return "#999";
            }
        })
        .on("mouseover", showedgeinfo)
        .on("mouseout", removeinfo);

    node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("r", function (d) {
            if (d.nstrains == 0)
                return 2;
            else
                return 2 * (1 + Math.log(d.nstrains));
        })
        .attr("stroke-width", 0.1)
        .attr("fill", function (d) {
            if (d.nodetype == "mf")
                return "#AAAAAA";
            else
                return color(d.gcftype);
        })
        .on("mouseover", showinfo)
        .on("mouseout", removeinfo)
        .on("click", selectnode)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    var current = undefined;

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function showedgeinfo(d) {
        gcfid = 0;
        mfid = 0;
        if (d.source.nodetype == 'gcf') {
            gcfid = d.source.dbid;
            mfid = d.target.dbid;
        } else {
            gcfid = d.target.dbid;
            mfid = d.source.dbid;
        }
        st = d.source.id + " <-> " + d.target.id;
        document.getElementById("infodiv").innerHTML = st;
        d3.json('/linker/get_overlap_strains/' + gcfid + '/' + mfid, function (error, strains) {
            a = document.getElementById("infodiv").innerHTML;
            a += " " + strains.strains.length + " strains, p = " + strains.p + " (";
            for (i = 0; i < strains.strains.length; i++) {
                a += strains.strains[i];
                if (i < strains.strains.length - 1)
                    a += ',';
            }
            a += ")";
            document.getElementById("infodiv").innerHTML = a;
        });
    }

    function showinfo(d) {
        infodiv = document.getElementById("infodiv");
        if (d.nodetype == 'mf') {
            var st = d.id;
            infodiv.innerHTML = st;
            d3.json('/linker/get_mf_strains/' + d.dbid, function (error, strains) {
                st = " " + strains.strains.length + " strains (";
                for (i = 0; i < strains.strains.length; i++) {
                    st += strains.strains[i];
                    if (i < strains.strains.length - 1)
                        st += ',';
                }

                st += ")";
                infodiv = document.getElementById("infodiv");
                a = infodiv.innerHTML;
                a += st;
                infodiv.innerHTML = a;
            });
        } else {
            st = d.id + " <b>" + d.gcftype + "</b> ";
            infodiv.innerHTML = st
            d3.json('/linker/get_gcf_strains/' + d.dbid, function (error, strains) {
                st = " " + strains.strains.length + " strains (";
                for (i = 0; i < strains.strains.length; i++) {
                    st += strains.strains[i];
                    if (i < strains.strains.length - 1)
                        st += ',';
                }
                st += ")";
                infodiv = document.getElementById("infodiv");
                a = infodiv.innerHTML;
                a += st;
                infodiv.innerHTML = a;
            });
        }

    }

    function selectnode(d) {

        sel = d3.select(this); // the currently selected node
        if (sel.classed("selected")) {

            /*
            if already selected, then:
            - unselect the current node
            - set opacity of all circles to 100%
            - remove the current search term from data table
             */

            sel.classed("selected", false);
            d3.selectAll("circle").attr("opacity", 1.0);
            table.search("").draw();

        } else {

            /*
            otherwise:
            - make the current node selected
            - set opacity of all circles to 50%
            - set the current node id as the search term for data table
             */

            sel.classed("selected", true);
            d3.selectAll("circle").attr("opacity", 0.50);
            sel.attr("opacity", 1.0);
            table.search(d.id).draw();

        }

    }

    function removeinfo() {
        infodiv = document.getElementById("infodiv");
        infodiv.innerHTML = "&nbsp;";
    }

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("cx", function (d) {
                return d.x;
            })
            .attr("cy", function (d) {
                return d.y;
            });

    }

    simulation.restart();
    $('#msg').text("");

});


// function dragstart(d) {
//    d3.select(this).classed("fixed", d.fixed = true);
//  }
//  function zoomed() {
//      nodeArea.attr('transform',
//              'translate(' + d3.event.translate + ') scale(' + d3.event.scale + ')');
//      console.log('zooming');
//  }


function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}