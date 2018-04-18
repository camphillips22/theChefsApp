function initGraph() {
    var margin = {top: 0, bottom: 20, left: 100, right: 100};
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

    rec_tip = d3.tip().attr('class', 'd3-tip')
      .html(function(d) { return d.recipe_name; })
      .offset([-10, 0])
      .direction(function(d) { return (this.getBBox().y > 0) ? 's' : 'n';})

    svg.call(rec_tip);
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

function wrap(text) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > 2*text.datum().r) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", lineHeight + "em").text(word);
      }
    }
  });
}

function showRecipes(data) {
  tip.hide();
  nodes = data['results'];
  var padding = 4, // separation between same-color nodes
    clusterPadding = 6, // separation between different-color nodes
    maxRadius = 12;

  d3.map(nodes, function(d) { d.radius = 5; d.cluster = parseInt(d.id)+1;});
  nested = d3.nest()
    .key(function(d) { return d.id;})
    .entries(nodes);

  var clusters = new Array(nested.length);
  nested.map(function(d) { clusters[+d.key + 1] = d.values[0]})

  color = d3.scale.category10()
      .domain(d3.range(nested.length));

  new_pack = d3.layout.pack()
    .sort(null)
    .size([width, height])
    .children(function(d) { return d.values; })
    .value(function(d) { return d.radius * d.radius; });
  new_pack
    .nodes({values: nested});

  svg.selectAll(".group").data([]).exit().remove();

  node = svg.selectAll(".group")
    .data(nodes)

  var new_nodes = node.enter().append("g")
      .attr("class", "group")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })

  new_nodes.append("circle")
    .style("fill", function(d) { return color(d.cluster); });
  new_nodes.append("text");

  node.select("circle")
    .attr("r", function(d) {return d.r})
    .on("mouseover", rec_tip.show)
    .on("mouseout", rec_tip.hide);
/*
  node.transition()
    .duration(750)
    .delay(function(d, i) { return i * 5; })
    .attrTween("r", function(d) {
      var i = d3.interpolate(0, d.r);
      return function(t) { return d.r = i(t); };
    });
*/
 node.select("text").style("font-size", "");

  node.select("text")
    .text(function(d) { return d.recipe_name; })
    .style("opacity", function(d) {  return d.r > 10 ? 1 : 0;})
    .attr("dy", "0em")
    .call(wrap);

   node.select("text").style("font-size", "");
  node.select("text")
    .attr("y", function(d) {
      return -0.5*(d3.select(this).selectAll("tspan").size()-1) + "em";
    }).style("font-size", function(d) {
      return Math.min(2*d.r, (2*d.r - 8) / this.getComputedTextLength()*24) + "px";
    })

  node.on("mouseover", onMouseOver);
  node.on("mouseout", onMouseOut);
  node.on("click", onClick);

  function onClick(d, i) {
  if (d._r) {
    d.r = d._r;
    d._r = null;
  } else {
    d._r = d.r;
    d.r = 150;
    svg.selectAll(".group").sort(function (a, b) {
      if (a._r) return 1;
      else return -1;
    });
  }


    node.select("circle").transition().duration(300)
    .attr("r", function(d) { return d.r;});
  }


  function onMouseOver(d, i) {

/*
    new_pack.nodes({values: nested})
  var node = d3.selectAll(".group").data(nodes);
  node.transition()
    .duration(300)
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
    */


  }

  function onMouseOut(d, i) {
    if (d._r) {
      d.r = d._r;
      d._r = null;
    }

    /*
  new_pack.nodes({values: nested});
  var node = d3.selectAll(".group").data(nodes);
  node.transition()
    .duration(300)
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
*/
  node.select("circle").transition().duration(300)
    .attr("r", function(d) { return d.r;});
  }
}
