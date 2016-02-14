var Network = function() {
  this.load = function(selector, data) {
    var network = this;
    this.dom_node = $(selector);
    this.width = this.dom_node.width() - 10;
    this.height = this.dom_node.height() - 10;

    this.cutoff_slider = d3.slider()
      .min(0.01)
      .max(1)
      .value(0.54)
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
    this.linked_nodes_only.property("checked", true);
    this.linked_nodes_only.on("change", function(value) {
      this.update();
    }.bind(this));

    this.picture_nodes_only = d3.select("#picture-nodes-only");
    this.picture_nodes_only.property("checked", true);
    this.picture_nodes_only.on("change", function(value) {
      this.update();
    }.bind(this));

    this.allow_pinning = d3.select("#allow-pinning");
    this.allow_pinning.property("checked", false);
    this.allow_pinning.on("change", function(value) {
      if (!value) {
        this.force.nodes().forEach(function(n) {
          n.fixed = false;
        });
        this.force.resume();
      }
    }.bind(this));

    this.svg = d3.select(selector).append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

    function zoom() {
      if (d3.event.defaultPrevented) return;
      this.graph.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }

    this.node_double_click = function(d) {
      d3.event.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = false);
      network.force.resume();
    }

    this.initial_zoom = this.height / 500;
    var zoom = d3.behavior.zoom()
      .scaleExtent([0.2, 8])
      .on("zoom", zoom.bind(this))
      .translate([(this.width - this.initial_zoom * this.width) / 2,
                  (this.height - this.initial_zoom * this.height) / 2])
      .scale(this.initial_zoom);

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
    shadow.append("feBlend")
      .attr("in", "SourceGraphic")
      .attr("in2", "blurOut")
      .attr("mode", "normal");

    var shadow_high = this.defs.append("filter")
      .attr("id", "shadow-high")
      .attr("x", "-20%")
      .attr("y", "-20%")
      .attr("width", "200%")
      .attr("height", "200%");
    shadow_high.append("feOffset")
      .attr("result", "offsetOut")
      .attr("in", "SourceAlpha")
      .attr("dx", 10)
      .attr("dy", 10);
    shadow_high.append("feGaussianBlur")
      .attr("result", "blurOut")
      .attr("in", "offsetOut")
      .attr("stdDeviation", 1);
    shadow_high.append("feColorMatrix")
      .attr("result", "shadowOut")
      .attr("in", "blurOut")
      .attr("values", "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .5 0");
    shadow_high.append("feBlend")
      .attr("in", "SourceGraphic")
      .attr("in2", "shadowOut")
      .attr("mode", "normal");

    this.pattern_id = 1;

    this.graph = this.svg
      .append("g")
      .call(zoom)
      .append("g")
      .attr("transform",
            "translate(" + (this.width - this.initial_zoom * this.width) / 2 + "," +
                           (this.height - this.initial_zoom * this.height) / 2 + ")" +
            "scale(" + this.initial_zoom + ")");

    this.banner_bar = this.svg.append("g");

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
      if (d.type == "intermediate") {
        return;
      }
      d3.event.sourceEvent.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = true);
    }

    function dragend(d) {
      if (d.type == "intermediate") {
        return;
      }
      d3.event.sourceEvent.stopPropagation();
      if (!network.allow_pinning.property("checked")) {
        d.fixed = false;
      }
    }

    this.drag = this.force.drag()
      .on("dragstart", dragstart)
      .on("dragend", dragend);

    this.load_data(data);
    this.update();
  }

  this.add_image = function(path, aspect_ratio) {
    var new_id = "pattern_" + this.pattern_id;
    if (!aspect_ratio) {
      aspect_ratio = 1;
    }
    var size = 100;
    this.pattern_id += 1;
    this.defs.append("svg:pattern")
      .attr("id", new_id)
      .attr("x", "0%")
      .attr("y", "0%")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr("viewBox", "0 0 " + size + " " + (size * aspect_ratio))
      .append("svg:image")
      .attr("xlink:href", path)
      .attr("width", size)
      .attr("height", size * aspect_ratio)
      .attr("x", "0%")
      .attr("y", "0%");

    return new_id;
  }

  this.load_data = function(data) {
    this.data = data;
    this.all_nodes = this.data.nodes.slice();
    this.all_edges = this.data.edges.slice();
    this.node_map = {};
    this.group_map = {};

    this.data.groups.forEach(function(g) {
      this.group_map[g.id] = g;

      if (g.image) {
          g.image_id = this.add_image(g.image, 1.5);
      }
    }.bind(this));

    this.banner_buttons = this.data.groups.filter(function(g) {
      return g.image;
    })
    this.banner = this.banner_bar.selectAll("g.banner")
        .data(this.banner_buttons, function(d) { return d.id; });

    this.banner_width = 30 * this.initial_zoom;
    this.banner_height = 45 * this.initial_zoom;
    this.banner_space = 10 * this.initial_zoom;
    this.banner_bar_position = {
      x: (this.width - this.banner_buttons.length *
             (this.banner_width + this.banner_space) - this.banner_space) / 2,
      y: 10 * this.initial_zoom,
    };

    this.banner.enter().append("g")
      .attr("id", function(d) { return "banner_" + d.id; })
      .attr("class", "banner")
      .attr("transform", function(d, i) {
        return "translate(" +
          (this.banner_bar_position.x +
           i * (this.banner_width + this.banner_space)) +
          "," + this.banner_bar_position.y + ")scale(" + (this.banner_width / 100) + ")";

      }.bind(this))
      .append("path")
      .style("fill", function(d, i) {
          return 'url(#' + d.image_id + ')';
      })
      .style("filter", "url(#shadow-high)")
      .attr("d", "m 99.523233,0.06290596 c 0.26113,21.26875304 0.24596,42.53749304 0,63.80624304 -0.23922,20.48887 -1.0327,36.480561 -8.17061,48.980061 -8.598528,15.0601 -22.924919,25.9306 -41.351779,36.6105 -18.430237,-10.6799 -32.754939,-21.5482 -41.3534688,-36.6105 -7.139609,-12.5039 -7.93477203,-28.493351 -8.17062003,-48.980061 -0.245961,-21.26875 -0.261128,-42.53749 0,-63.80624304 z")

    this.banner.exit().remove();

    this.all_nodes.forEach(function(n) {
      n.x = Math.floor(this.width / 2 + Math.random() * 100);
      n.y = Math.floor(this.height / 2 + Math.random() * 100);
      n.radius = 15;
      n.weight = 1;

      if (n.image) {
          n.image_id = this.add_image(n.image);
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

      if (s.image && t.image) {
        // if both real nodes have an image, then just set a flag here,
        // so the intermediate node also is included when only non-image
        // nodes are shown
        i.image = true;
      }

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

      if (this.picture_nodes_only.property("checked") &&
          (!s.image || !t.image)) {
        return;
      }

      links.push({source: s, target: i, value: e.value, normalized_value: e.normalized_value},
                 {source: i, target: t, value: e.value, normalized_value: e.normalized_value});
      edges.push(e);
      linked_node_map[s.id] = s;
      linked_node_map[t.id] = t;
      linked_node_map[i.id] = i;
    }.bind(this));

    var nodes = [];
    this.all_nodes.forEach(function(n) {
      if (this.linked_nodes_only.property("checked") && !linked_node_map[n.id]) {
        return;
      }

      if (this.picture_nodes_only.property("checked") && !n.image) {
        return;
      }

      nodes.push(n);
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
      .attr("stroke", "#ddd")
      .attr("stroke-opacity", 0.7)
      .attr("stroke-width", function(d) {
        return d.value * 8 / this.max_edge_value;
      }.bind(this));

    this.link.exit().remove();

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
      .attr("r", function(d) {
        if (d.hover) {
          return 1.2 * d.radius;
        }
        return d.radius;
      })
      .style("stroke", function(d) { return d.color || "#999"; })
      .style("stroke-width", 1.0)
      .style("fill", function(d) {
        if (d.image_id) {
          return 'url(#' + d.image_id + ')';
        } else {
          return "#777";
        }
      })
      .style("filter", "url(#shadow)")
      .on("dblclick", this.node_double_click)
      .call(this.drag)
      .on("mouseover", function(d) {
        d.hover = true;
        this.node.attr("r", function(d) {
          if (d.hover) {
            return 1.2 * d.radius;
          }
          return d.radius;
        });
      }.bind(this))
      .on("mouseout", function(d) {
        d.hover = false;
        this.node.attr("r", function(d) {
          if (d.hover) {
            return 1.2 * d.radius;
          }
          return d.radius;
        });
      }.bind(this));

    this.node.append("title")
      .text(function(d) { return d.name; });

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
