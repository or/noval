var Network = function() {
  this.load = function(selector, data) {
    var network = this;
    this.dom_node = $(selector);
    this.width = this.dom_node.width() - 10;
    this.height = this.dom_node.height() - 10;

    this.cutoff_slider = d3.slider()
      .min(0.01)
      .max(1)
      .value(0.5)
      .orientation("vertical")
      .on("slide", function(evt, value) {
        this.update();
      }.bind(this));

    d3.select("#cutoff-slider").call(this.cutoff_slider);

    this.charge_slider = d3.slider()
      .min(-10)
      .max(-500)
      .value(-70)
      .on("slide", function(evt, value) {
        this.force_update();
      }.bind(this));

    d3.select("#charge-slider").call(this.charge_slider);

    this.link_distance_slider = d3.slider()
      .min(10)
      .max(80)
      .value(30)
      .on("slide", function(evt, value) {
        this.force_update();
      }.bind(this));

    d3.select("#node-distance-slider").call(this.link_distance_slider);

    this.linked_nodes_only = d3.select("#linked-nodes-only");
    this.linked_nodes_only.on("change", function(value) {
      this.update();
    }.bind(this));

    function zoom() {
      if (d3.event.defaultPrevented) return;
      this.graph.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }

    this.node_double_click = function(d) {
      d3.event.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = false);
      network.force.start();
    }

    var zoom = d3.behavior.zoom()
      .scaleExtent([1, 8])
      .on("zoom", zoom.bind(this));

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

    this.force_update = function() {
      this.force
        .size([this.width, this.height])
        .gravity(0.1)
        .charge(function(d) {
          var value = d.edge_value_sum || 0;
          var v = value / network.max_edge_value_sum;
          v = Math.sqrt(v);
          v = Math.sqrt(v);
          return network.charge_slider.value() * (1 + v);
        })
        .linkStrength(function(d) {
          return 0.5 + 1 * d.normalized_value;
        })
        .linkDistance(function(d) {
          return network.link_distance_slider.value() * (1.5 - d.normalized_value);
        })

      this.force.start();
    }

    this.force = d3.layout.force()
      .on("tick", function() {
        this.link.attr("d", function(d) {
          return "M" + d.source.x + "," + d.source.y
            + "S" + d.intermediate.x + "," + d.intermediate.y
            + " " + d.target.x + "," + d.target.y;
        });

        this.node
          .attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
      }.bind(this));

    this.force_update();

    function dragstart(d) {
      d3.event.sourceEvent.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = true);
    }

    this.drag = this.force.drag()
      .on("dragstart", dragstart);

    this.load_data(data);
    this.update();
  }

  this.load_data = function(data) {
    this.data = data;
    this.all_nodes = this.data.nodes.slice();
    this.all_edges = this.data.edges.slice();
    this.node_map = {};

    this.all_nodes.forEach(function(n) {
      n.x = Math.floor(this.width / 2 + Math.random() * 100);
      n.y = Math.floor(this.height / 2 + Math.random() * 100);
      n.radius = 15;
      n.weight = 1;

      if (n.image) {
        n.image_id = "pattern_" + this.pattern_id;
        var size = 100;
        this.pattern_id += 1;
        this.defs.append("svg:pattern")
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
      this.node_map[n.id] = n;

      n.edge_value_sum = 0;
    }.bind(this));

    this.max_edge_value = 0;
    this.all_edges.forEach(function(e) {
      this.max_edge_value = Math.max(this.max_edge_value, e.value);
    }.bind(this));

    this.max_edge_value_sum = 0;
    this.all_edges.forEach(function(e) {
      var s = this.node_map[e.from],
          t = this.node_map[e.to],
          i = {id: s.id + "_" + t.id,
               type: "intermediate"}; // intermediate node

      i.x = (s.x + t.x) / 2;
      i.y = (s.y + t.y) / 2;

      var v = e.value / this.max_edge_value;
      v = Math.sqrt(v);
      v = Math.sqrt(v);
      if (v < 0.01) {
        v = 0.01;
      } else if (v > 0.99) {
        v = 1.0;
      }
      e.normalized_value = v;

      this.all_nodes.push(i);
      e.source = s;
      e.target = t;
      e.intermediate = i;

      e.source.edge_value_sum += e.value;
      e.target.edge_value_sum += e.value;

      this.max_edge_value_sum = Math.max(this.max_edge_value_sum, e.source.edge_value_sum);
      this.max_edge_value_sum = Math.max(this.max_edge_value_sum, e.target.edge_value_sum);
    }.bind(this));
  }

  this.update = function() {
    var edges = [];
    var links = [];
    var linked_node_map = {};
    this.all_edges.forEach(function(e) {
      var s = e.source,
          t = e.target,
          i = e.intermediate;

      if (e.normalized_value < 1 - this.cutoff_slider.value()) {
        return;
      }

      links.push({source: s, target: i, value: e.value, normalized_value: e.normalized_value},
                 {source: i, target: t, value: e.value, normalized_value: e.normalized_value});
      edges.push(e);
      linked_node_map[s.id] = s;
      linked_node_map[t.id] = t;
      linked_node_map[i.id] = i;
    }.bind(this));

    this.force.links(links);

    if (this.link) {
      this.link.remove();
    }
    this.link = this.graph.selectAll("line.link")
      .data(edges, function(d) { return d.source.id + "_" + d.target.id; });

    this.link.enter().append("path")
      .attr("class", "link")
      .attr("fill", "none")
      .attr("stroke", "#fff")
      .attr("stroke-opacity", 0.8)
      .attr("stroke-width", function(d) {
        return d.value * 8 / this.max_edge_value;
      }.bind(this));

    this.link.exit().remove();

    var nodes;
    if (this.linked_nodes_only.property("checked")) {
      nodes = [];
      for (var key in linked_node_map) {
        nodes.push(linked_node_map[key]);
      }
    } else {
      nodes = this.all_nodes.slice();
    }
    this.force.nodes(nodes);

    if (this.node) {
      this.node.remove();
    }
    this.node = this.graph.selectAll("circle.node")
      .data(nodes, function(d) { return d.id; });

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

    this.node.append("title")
      .text(function(d) { return d.title; });

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
