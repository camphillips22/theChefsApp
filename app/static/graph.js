
var mymenu = [
  {
    title: 'Next Page',
    action: function(d, i) {
      updatePage(d.cluster, d.page + 1);
    },
    disabled: function(d) { return d.page == active_pages[d.cluster].max;}
  },
  {
    title: 'Previous Page',
    action: function(d, i) {
      updatePage(d.cluster, d.page - 1);
    },
    disabled: function(d) { return !d.page; }
  }
]

var tourComplete = false;
var tourStarted = false;

var cluster_menu = [
  {
    title: function(d) {
      if(d.value > 3000) return 'Too many recipes to show. Choose another bubble first.';
      else return 'View Recipes';
    },
    action: function(d, i) {
      appendFilter(d.id, d.name);
      var form_dat = $("#filter_form").serialize();
      form_dat += (form_dat.length > 0 ? "&" : "") + "grouping=similarity";
      $.ajax({
        type: "POST",
        url: "/cluster_filter",
        data:  form_dat,
        success: function(data) {
          console.log(data);
          if (data.results[0].name == '')
            showRecipes(data);
          else
            onGroupData(data);
        },
      });
    },
    disabled: function(d, i) { return d.value > 3000}
  },
]

function startTour() {

    var tour = {
      id: "hopscotch-tour",
      showPrevButton: "true",
      nextOnTargetClick: "true",
      onEnd: function() {
        tourComplete = true;
      },
      onClose: function() {
        tourComplete = true;
      },   
      onStart: function() {
        tourStarted = true;
      },            
      steps: [
        {
          title: "Welcome to The Chef's App",
          content: "This tutorial will guide you through the features of this tool. If you close this tutorial by accident, just reload the page to walk through it again. Click Next to continue.",
          target: "#app_name",
          placement: "right"
        },
        {
          title: "About this tool",
          content: "This tool is the product of a research effort at the Georgia Institute of Technology. Our goal is to help people explore the enormous number of recipes out there, and help them plan exciting, healthy meals, and show them foods they didn't even know they wanted!",
          target: "#app_name",
          placement: "right"
        },
        {
          title: "About this tool",
          content: "Because this is a research-grade tool, you may experience bugs or slow loading. Also, please note that our recipe details currently only show ingredients, but not the cooking method.",
          target: "#app_name",
          placement: "right"
        },                 
        {
          title: "Filtering Recipes",
          content: "You can start typing in any of these boxes to filter recipes. If you have a dietary restriction, enter it here.",
          target: ["#diet_select","#app_name"],
          placement: "right",
          xOffset: "200"
        },
        {
          title: "Searching Recipes",
          content: "Filters are great for when know exactly what you want. For example, if you're craving artichokes, just start typing artichokes here! But, this app is best at helping you find foods you don't even know you want, so let's explore!",
          target: ["#ingredient_name","#app_name"],
          placement: "right",
          xOffset: "200"
        },    
        {
          title: "Grouping Recipes",
          content: "Each bubble you see to the right is called a Group. This represents a bunch of recipes that are similar in some way: Mexican recipes, soups, breakfasts, etc.",
          target: ["#group_sidebar_title", "#app_name"],
          placement: "right"
        },
        {
          title: "Group Order",
          content: "The types of group that you see are controlled by this list. The top group is the one you see when the page loads. That's why you see recipes by ethnicity right now.",
          target: ["#ethnicity_rank","#app_name"],
          placement: "right"
        },
        {
          title: "Group by Recipe Type",
          content: "Let's change this up! Say you don't care what cuisine you're going to make, but you really want some kind of pizza! Drag Recipe Type to the top of the list to view the Pizza category. It may take a few seconds to load.",
          target: ["#recipe_type_rank","#app_name"],
          placement: "right"
        },                 
        {
          title: "Pizza!",
          content: "There's Pizzas and calzones!",
          target: ["#circle_Pizza_and_calzones","#app_name"],
          placement: "right"
        },   
        {
          title: "Pro Tip",
          content: "You could have also searched for pizzas in the Filter sidebar to get here.",
          target: ["#type_select","#app_name"],
          placement: "right",
          xOffset: "200"
        },
        {
          title: "Group Pizza by Ethnicity",
          content: "It's 2018, and pizzas can come from many world cuisines! Because Ethnicity is in 2nd place in the list, you'll see all pizzas by cuisine when you click the Pizza group.",
          target: ["#ethnicity_rank","#app_name"],
          placement: "right"
        },
        {
          title: "Group Pizza by Ethnicity",
          content: "Click on the Pizza group to break them up by ethnicity.",
          target: ["#circle_Pizza_and_calzones","#app_name"],
          placement: "right"
        },                                            
        {
          title: "Changing Group Order",
          content: "Your pizza recipes are now divided up by ethnicity! Now, let's actually check out some pizza recipes! Right click on the Italian group and select View Recipes.",
          target: ["#circle_Italian","#app_name"],
          placement: "right"
        },
        {
          title: "View Recipe Clusters",
          content: "Each bubble is now a recipe. The colored groups indicate similar recipes. If you've been following along, you should have one cluster for calzones, one for traditional pizzas, and one group with non-traditional and sweet toppings.",
          target: "#app_name",
          placement: "right"
        },
        {
          title: "Get Recipe Details",
          content: "Click on a recipe to view details.",
          target: ["recipe_node_Mozzarella_artichoke_and_pancetta_mini_pizzas","#app_name"],
          placement: "right"
        },
        {
          title: "See More Recipes",
          content: "If you like what you see in a cluster, but haven't found the perfect recipe yet, then right click any recipe and select Next Page. You'll get more like it.",
          target: ["recipe_node_Pizza_nutella","#app_name"],
          placement: "left"
        },
        {
          title: "Removing Groups",
          content: "If you want to go back to an earlier view, just click the red X next to any group name. For example, clicking X next to Ethnicity= Italian will bring you back to all pizzas by ethnicity, so you can check out that Greek pizza that you missed earlier.",
          target: ["recipe_type_rank","#app_name"],
          placement: "right"
        },
        {
          title: "Good luck!",
          content: "This concludes the tutorial. We hope you enjoy using TheChefsApp!",
          target: ["#app_name"],
          placement: "right"
        }                                                                                                   
      ]
    };

    //tourStarted = true;
    // Start the tour!
    hopscotch.startTour(tour);  
}

function initGraph() {
    var margin = {top: 0, bottom: 20, left: 100, right: 100};
      width = 960,
      height = 750;

		svg = d3.select("#graph").append("svg")
      .attr("height", height + margin.top + margin.bottom)
      .attr("width", width + margin.right + margin.left)
    .append("g")
      .attr("transform", "translate(" + [margin.left, margin.top] + ")");

    var popup = svg.append("g").attr("class", "popup")
    var poptext = popup.append("text")
    poptext.attr("y", "1.1em")
    poptext.append("tspan").attr("id", "ingredients")
      .attr("x", 0)
      .attr("dy", "1.1em")
    poptext.append("tspan").attr("id", "courses")
      .attr("x", 0)
      .attr("dy", "1.1em")
    popup.append("rect");

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

    info_tip = d3.tip()
      .attr('class', 'info-tip')
      .direction(function(d) {return d.x > width/2 ? 'w' : 'e';})
      .html(function(d) {
        console.log(d);
        if(d.recipe_info) {
          tmpText = '<strong>Ingredients:</strong><br/>'
          tmpText += d.recipe_info.ingredients.join('<br/>');
          if(d.recipe_info.ethnicities 
            && d.recipe_info.ethnicities.length > 0) {
            tmpText += '<br/><br/><strong>Cuisines:</strong><br/>'
            tmpText += d.recipe_info.ethnicities.join('<br/>');
          }
          if(d.recipe_info.courses
            && d.recipe_info.courses.length > 0) {
            tmpText += '<br/><br/><strong>Courses:</strong><br/>'
            tmpText += d.recipe_info.courses.join('<br/>');
          }
          if(d.recipe_info.diets
            && d.recipe_info.diets.length > 0) {
            tmpText += '<br/><br/><strong>Diets:</strong><br/>'
            tmpText += d.recipe_info.diets.join('<br/>');
          }
          if(d.recipe_info.occasions
            && d.recipe_info.occasions.length > 0) {
            tmpText += '<br/><br/><strong>Occasions:</strong><br/>'
            tmpText += d.recipe_info.occasions.join('<br/>');
          }      
          if(d.recipe_info.recipe_types
            && d.recipe_info.recipe_types.length > 0) {
            tmpText += '<br/><br/><strong>Category:</strong><br/>'
            tmpText += d.recipe_info.recipe_types.join('<br/>');
          }                                        
        } else {
          tmpText = d.recipe_name;
        }
        return tmpText;
      })

    svg.call(info_tip);
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
  tip.hide()
  rec_tip.hide()
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
      .attr("transform", function(d) { 
        return "translate(" + d.x + "," + -100 + ")"; });

  new_nodes.transition().duration(1000)
      .attr("transform", function(d) { 
        return "translate(" + d.x + "," + d.y + ")"; });

  new_nodes.append("circle");
  new_nodes.append("text")
    .style("opacity", 0)
    .attr("dy", ".35em");

  node.exit().transition().duration(500)
    .attr("transform", function(d) { 
      return "translate(" + d.x + "," + -100 + ")"; })
    .remove();
  node.transition()
    .duration(1000)
    .attr("transform", function(d) { 
      return "translate(" + d.x + "," + d.y + ")"; })

  node.select("circle")
    .style("fill", "#CDCDCD")
    .attr("id", function(d) {
      return "circle_" + clean_name(d.name);
    })
    .on("mouseover", null)
    .on("mouseout", null)
    .on("click", function(d) {
      appendFilter(d.id, d.name);
      submitFilters();
    });

  node.select("circle").transition().duration(1000)
    .attr("r", function(d) { return d.r; })

  sizeText(node.select("text"), 200, 700);

  node.on("mouseover", tip.show);
  node.on("mouseout", tip.hide);
  node.on("click", null);
  node.on("contextmenu", d3.contextMenu(cluster_menu));
}

function clean_name(text) {
  text = text.replace(/ /g, "_");
  text = text.replace(/&/g,"and");
  text = text.replace(/;/g,"");
  return text;
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
  if (page < 0) return null;
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
    .transition().duration(0)
      .attr("transform", "scale(1,1)")
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
  rec_tip.hide()
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
    .attr("id", function(d) {
      return "recipe_node_" + clean_name(d.recipe_name);
    })
    .on("mouseover", rec_tip.show)
    .on("mouseout", rec_tip.hide)
    .on("click", rec_tip.hide);

  sizeText(node.select("text"), 200, 500);

  node.on("mouseover", onMouseOver);
  node.on("mouseout", onMouseOut);
  node.on("click", onClick);
  node.on("contextmenu", d3.contextMenu(mymenu));

  function onClick(d) {
    if (d._r) {
      d.r = d._r;
      d._r = null;
      info_tip.hide();
    } else {
      d._r = d.r;
      d.r = 150;
      svg.selectAll(".group").sort(function (a, b) {
        if (a._r) return 1;
        else return -1;
      });

      var group = d3.select(this).node();

      $.post({
        url: '/get_recipe_info',
        data: 'recipe_id=' + d.recipe_id,
        success: function(msg) { 
          d.recipe_info = msg['results'][0]; 
          info_tip.show(d, i, group) ;}
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
      info_tip.hide();
      d3.select(this).select("circle").transition().duration(300)
        .attr("r", function(d) { return d.r;});
      sizeText(d3.select(this).select("text"), 0, 0);
    }
  }
}
