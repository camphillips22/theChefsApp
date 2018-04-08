function initGraph() {
    var margin = {top: 0, bottom: 20, left: 100, right: 100},
      width = 960,
      height = 960;

		svg = d3.select("#graph").append("svg")
      .attr("height", height + margin.top + margin.bottom)
      .attr("width", width + margin.right + margin.left)
    .append("g")
      .attr("transform", "translate(" + [margin.left, margin.top] + ")");

		pack = d3.layout.pack()
        .sort(function(a, b) { return b.value - a.value;})
		    .size([width-20, height-20])
		    .padding(4);

    tip = d3.tip().attr('class', 'd3-tip')
      .html(function(d) { return d.name; })
      .offset([-10, 0])
      .direction(function(d) { return (this.getBBox().y > 0) ? 's' : 'n';})

    svg.call(tip);
}


function onGroupData(data) {
  parsed_data = data["results"];

  parsed_data.forEach(function(d) {
    d.value = d.recipes.length;
  })

  root = {
    name: 'root',
    value: 1,
    children: parsed_data
  }

  pack_nodes = pack.nodes(root)

  var node = svg.selectAll(".group")
  .data(root.children);

  var new_nodes = node.enter().append("g")
      .attr("class", "group")
      .attr("transform", function(d) { return "translate(" + d.x + "," + -100 + ")"; });

  new_nodes.transition().duration(1000)
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

  new_nodes.append("circle");
  new_nodes.append("text");

  node.exit().transition().duration(500)
    .attr("transform", function(d) { return "translate(" + d.x + "," + -100 + ")"; })
    .remove();
  node.transition()
    .duration(1000)
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })

  node.select("circle")
    .attr("id", function(d) { return d.id; })
    .attr("r", function(d) { return d.r; })
    .style("fill", "rgba(31, 119, 180, 0)")
    .style("stroke", "black")
    .on("click", function(d) {
      appendFilter(d.id, d.name);
      submitFilters();
    });

  node.select("text").style("font-size", "");

  node.select("text")
    .text(function(d) { return d.name; })
    .style("opacity", function(d) {  return d.r > 10 ? 1 : 0;})
    .style("font-size", function(d) {
          return Math.min(2*d.r, (2*d.r - 8) / this.getComputedTextLength()*24) + "px";
    })
    .attr("dy", ".35em");

  node.on("mouseover", tip.show);
  node.on("mouseout", tip.hide);
}
