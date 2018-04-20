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


function sizeText(texts, dur, delay) {

  texts
    .style("opacity", 0)
    .text(function(d) { return d.recipe_name || d.name; })
    .attr("dy", ".35em")
    .style("font-size", "")
    .call(wrap);

  texts
    .style("font-size", function(d) {
      var bb = this.getBBox();
      return Math.min(2*d.r, (2*d.r - 8) / Math.hypot(bb.width, bb.height)*24) + "px";
    }).attr("y", function(d) {
      return -0.5*(d3.select(this).selectAll("tspan").size()-1) + "em";
    })

  texts.transition().duration(dur).delay(delay)
    .style("opacity", function(d) {  return d.r > 10 ? 1 : 0;})

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
  new_nodes.append("text")
    .style("opacity", 0)
    .attr("dy", ".35em");

  node.exit().transition().duration(500)
    .attr("transform", function(d) { return "translate(" + d.x + "," + -100 + ")"; })
    .remove();
  node.transition()
    .duration(1000)
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })

  node.select("circle")
    .style("fill", "#CDCDCD")
    .on("click", function(d) {
      appendFilter(d.id, d.name);
      submitFilters();
    });

  node.select("circle").transition().duration(1000)
    .attr("r", function(d) { return d.r; })

  sizeText(node.select("text"), 200, 700);

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
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > 2*text.datum().r && words.length) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("dy", lineHeight + "em").text(word);
      }
    }
  });
}

function pageNodes() {
  return d3.nest()
    .key(function(d) { return d.id;})
    .rollup(function(v) {
      var paged = v.filter(function(d) { return d.page == active_pages[d.cluster].current; })
      return paged;})
    .entries(nodes);
}

function updatePage(clust, page) {
  tip.hide();
  active_pages[clust].current = Math.min(active_pages[clust].max, page);

  var cnode_select = d3.selectAll(".group")
    .filter(function(d) {return d.cluster==clust;});

  cnode = cnode_select
    .data(
      nodes.filter(function(d) {
        return d.cluster == clust && d.page == active_pages[clust].current})
    );

  cnode.exit().selectAll("circle, text").transition().duration(500)
    .attr("transform", "scale(0, 1)");

  cnode.selectAll("circle, text")
    .attr("transform", "scale(1, 1)")

  cnode.selectAll("circle").transition().delay(500).duration(500)
    .attr("transform", "scale(1, 1)")
    .attr("opacity", 1);

  sizeText(cnode.select("text"), 300, 700);

  cnode.select("circle").transition().duration(1000)
    .attr("transform", "scale(-1, 1)")
    .transition().duration(0).attr("transform", "scale(1,1)");
}

function pack_pages(data, page_size) {

  var clusterCounters = {};

  d3.map(nodes, function(d) {
    d.radius = 5;
    d.cluster = parseInt(d.id)+1;
    if (!clusterCounters[d.cluster]) {
      clusterCounters[d.cluster] = 0;
      active_pages[d.cluster] = {max: 0, current: 0};
    }
    d.idx = clusterCounters[d.cluster] % page_size;
    d.page = Math.floor(clusterCounters[d.cluster]++/page_size);
    active_pages[d.cluster].max = Math.max(d.page, active_pages[d.cluster].max);
  });

  var nested = pageNodes();

  var cluster_pack = d3.layout.pack()
    .sort(null)
    .size([width, height])
    .padding(4)
    .children(function(d) { return d.values; })
    .value(function(d) { return d.radius * d.radius; });

  cluster_pack
    .nodes({values: nested});

  d3.map(nodes, function(d) {
    if (d.page != 0) {
      var lnode = nodes.find(function(dd) {
        return dd.page == 0 && dd.id == d.id && dd.idx === d.idx});
      d.x = lnode.x;
      d.y = lnode.y;
      d.r = lnode.r;
    }
  })
}

function showRecipes(data) {
  tip.hide();
  nodes = data['results'];
  var padding = 4, // separation between same-color nodes
    clusterPadding = 6, // separation between different-color nodes
    maxRadius = 12,
    page_size = 7;

  active_pages = {};

  var colors = [
    '#DC4B34',
    '#967483',
    '#CFDF64',
    '#99CCAB',
    '#FAEEC5',
    '#F59192',
    '#F4B14F',
    '#F3CF13'
  ]

  var nClust = d3.map(nodes, function(d) { return d.id; }).size();

  color = d3.scale.ordinal()
      .domain(d3.range(nClust))
      .range(colors);

  pack_pages(nodes, page_size);

  view_nodes = nodes.filter(function(d) {
    return active_pages[d.cluster].current == d.page;
  })

  node = svg.selectAll(".group")
    .data(view_nodes)

  node.exit().transition().duration(500)
    .attr("transform", function(d) { return "translate(" + d.x + "," + -100 + ")"; })
    .remove();
  node.transition()
    .duration(1000)
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })

  var new_nodes = node.enter().append("g")
      .attr("class", "group")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })

  new_nodes.append("circle")
  new_nodes.append("text");

  node.select("circle").transition().duration(500)
    .attr("r", function(d) {return d.r})
    .style("fill", function(d) { return color(d.cluster); });

  node.select("circle")
    .on("mouseover", rec_tip.show)
    .on("mouseout", rec_tip.hide)
    .on("click", rec_tip.hide);

  sizeText(node.select("text"), 200, 500);

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

    d3.select(this).select("circle").transition().duration(300)
    .attr("r", function(d) { return d.r;});

    sizeText(d3.select(this).select("text"), 200, 100);
  }

  function onMouseOver(d, i) {
  }

  function onMouseOut(d, i) {
    if (d._r) {
      d.r = d._r;
      d._r = null;
    }

    d3.select(this).select("circle").transition().duration(300)
      .attr("r", function(d) { return d.r;});
    sizeText(d3.select(this).select("text"), 0, 0);
  }
}
