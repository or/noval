var Network = function() {
  this.load = function(selector, data) {
    this.dom_node = $(selector);
    this.width = this.dom_node.width() - 10;
    this.height = this.dom_node.height() - 10;

    var network = this;

    function zoom() {
      if (d3.event.defaultPrevented) return;
      network.graph.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
    var zoom = d3.behavior.zoom()
      .scaleExtent([1, 8])
      .on("zoom", zoom);

    this.svg = d3.select(selector).append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

    this.defs = this.svg.append('svg:defs');
    var shadow = this.defs.append("filter")
      .attr("id", "shadow")
      .attr("x", "-20%")
      .attr("y", "-20%")
      .attr("width", "200%")
      .attr("height", "200%");
    shadow.append("feOffset")
      .attr("result", "offsetOut")
      .attr("in", "SourceAlpha")
      .attr("dx", 1)
      .attr("dy", 1);
    shadow.append("feGaussianBlur")
      .attr("result", "blurOut")
      .attr("in", "offsetOut")
      .attr("stdDeviation", 1);
    /*var merge = shadow.append("feMerge");
    merge.append("feMergeNode")
      .attr("in", "blurOut");
    merge.append("feMergeNode")
      .attr("in", "SourceGraphic");*/
    shadow.append("feBlend")
      .attr("in", "SourceGraphic")
      .attr("in2", "blurOut")
      .attr("mode", "normal");

    this.pattern_id = 1;

    this.graph = this.svg
      .append("g")
      .call(zoom)
      .append("g");

    this.graph.append("rect")
      .attr("x", -10000)
      .attr("y", -10000)
      .attr("width", 20000)
      .attr("height", 20000)
      .style("fill", "none")
      .style("pointer-events", "all");

    this.linksG = this.graph.attr("id", "links");
    this.nodesG = this.graph.attr("id", "nodes");

    this.force = d3.layout.force()
      .size([this.width, this.height])
      .charge(-100)
      .linkDistance(50)
      .linkStrength(1.5)
      .on("tick", function() {
        network.link.attr("d", function(d) {
          return "M" + d.source.x + "," + d.source.y
            + "S" + d.intermediate.x + "," + d.intermediate.y
            + " " + d.target.x + "," + d.target.y;
        });

        network.node
          .attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
      });

    this.node_double_click = function(d) {
      d3.event.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = false);
      network.force.start();
    }

    function dragstart(d) {
      d3.event.sourceEvent.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = true);
    }

    this.drag = this.force.drag()
      .on("dragstart", dragstart);

    this.load_data(data);
    this.update();
  }

  this.build_node_map = function(nodes) {
    this.node_map = {};
    var network = this;
    nodes.forEach(function (n) {
      network.node_map[n.id] = n;
    });
  }

  this.load_data = function(data) {
    var network = this;

    this.data = data;
    this.data.nodes.forEach(function(n) {
      n.x = Math.floor(network.width / 2 + Math.random() * 100);
      n.y = Math.floor(network.height / 2 + Math.random() * 100);
      n.radius = 10;
      n.weight = 1;

      if (n.image) {
        n.image_id = "pattern_" + network.pattern_id;
        var size = 100;
        network.pattern_id += 1;
        network.defs.append("svg:pattern")
          .attr("id", n.image_id)
          .attr("x", "0%")
          .attr("y", "0%")
          .attr("width", "100%")
          .attr("height", "100%")
          .attr("viewBox", "0 0 " + size + " " + size)
          .append("svg:image")
          .attr("xlink:href", n.image)
          .attr("width", size)
          .attr("height", size)
          .attr("x", "0%")
          .attr("y", "0%");
      }
    });

    this.data.edges = this.data.edges.filter(function(e) {
      return e.flag != "cutoff";
    });

    this.build_node_map(this.data.nodes);

    this.edge_map = {}
    var network = this;
    this.max_edge_value = 0;
    this.data.edges.forEach(function (e) {
      e.source = network.node_map[e.from];
      e.target = network.node_map[e.to];
      network.max_edge_value = Math.max(network.max_edge_value, e.value);

      network.edge_map[e.source.id + "-" + e.target.id] = 1;
      network.edge_map[e.target.id + "-" + e.source.id] = 1;
    });
  }

  this.update = function() {
    var links = [];
    var nodes = this.data.nodes.slice();
    this.data.edges.forEach(function(e) {
      var s = e.source,
          t = e.target,
          i = {}; // intermediate node

      i.x = Math.floor(this.width / 2 + Math.random() * 100);
      i.y = Math.floor(this.height / 2 + Math.random() * 100);

      nodes.push(i);
      links.push({source: s, target: i}, {source: i, target: t});
      e.intermediate = i;
    });
    this.force.links(links);

    this.link = this.linksG.selectAll("line.link")
      .data(this.data.edges, function(d) { return d.source.id + "_" + d.target.id; });

    this.link.enter().append("path")
      .attr("class", "link")
      .attr("fill", "none")
      .attr("stroke", "#fff")
      .attr("stroke-opacity", 0.8)
      .attr("stroke-width", function(d) {
        return d.value * 8 / this.max_edge_value;
      }.bind(this))

    this.link.exit().remove();

    this.force.nodes(nodes);

    this.node = this.nodesG.selectAll("circle.node")
      .data(this.data.nodes, function(d) { return d.id; });

    this.node.enter().append("circle")
      .attr("id", function(d) { return "node_" + d.id; })
      .attr("class", "node")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", function(d) { return d.radius; })
      .style("stroke", function(d) { return d.color || "#999"; })
      .style("stroke-width", 1.0)
      .style("clip-path", function(d) { return "#circle"; })
      .style("fill", function(d) {
        if (d.image_id) {
          return 'url(#' + d.image_id + ')';
        } else {
          return "#777";
        }
      })
      .style("filter", "url(#shadow)")
      .on("dblclick", this.node_double_click)
      .call(this.drag);

    //node.on("mouseover", showDetails)
    //  .on("mouseout", hideDetails)

    this.node.exit().remove();

    this.force.start();
  }
}

function load_dialogues() {
  var network = new Network();
  document.network = network;

  jQuery.getJSON("data/dialogues.json", function(data) {
    network.load("#dialogues", data);
  });
}
