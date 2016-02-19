var DATA_PATH = "/data/";
var IMAGE_PATH = "/images/";
var BANNERS_PATH = IMAGE_PATH + "banners/";
var COVERS_PATH = IMAGE_PATH + "covers/";
var CHARACTERS_SMALL_PATH = IMAGE_PATH + "characters/small/";
var GRAVITY = 0.1;

var initial_configuration = [{"id":"bronn","x":582.4333273672327,"y":393.5839173228562},{"id":"oberyn_martell","x":610.1042604645922,"y":474.7111144978879},{"id":"tyrion_lannister","x":537.0464135687433,"y":456.6012375979708},{"id":"daenerys_targaryen","x":661.7255954248515,"y":546.764500721908},{"id":"brynden_tully","x":665,"y":535},{"id":"jaime_lannister","x":476.1718321399371,"y":391.95520255491533},{"id":"cersei_lannister","x":456.1262852452475,"y":460.6109465907577},{"id":"brienne_of_tarth","x":505.37843869311655,"y":313.48252242073295},{"id":"jorah_mormont","x":611.095632026659,"y":518.3247903096949},{"id":"asha_greyjoy","x":813.5351491697872,"y":563.6683177836819},{"id":"sandor_clegane","x":569.2543425576779,"y":300.6520280087628},{"id":"mance_rayder","x":774.301598584061,"y":270.67622484822823},{"id":"jon_snow","x":736.2415198288844,"y":334.2183002317025},{"id":"bowen_marsh","x":808.9186053402666,"y":355.8563159756841},{"id":"arya_stark","x":642.6662196995944,"y":330.06054303689376},{"id":"robb_stark","x":451.8421937318454,"y":277.51955252851604},{"id":"petyr_baelish","x":558.8809686601595,"y":548.3691545609149},{"id":"davos_seaworth","x":803.5693082212092,"y":434.2202305178319},{"id":"theon_greyjoy","x":801.9330446228516,"y":508.5030176947015},{"id":"varys","x":487.8122543395513,"y":498.42710178314337},{"id":"balon_greyjoy","x":824.7772221208339,"y":471.2631429666085},{"id":"joffrey_baratheon","x":722,"y":260},{"id":"pycelle","x":530.6573073314676,"y":612.1961335388239},{"id":"kevan_lannister","x":533.4993029256989,"y":374.3621265613936},{"id":"mordane","x":873,"y":600},{"id":"jory_cassel","x":912,"y":497},{"id":"catelyn_stark","x":432.9775639489536,"y":334.2012082562854},{"id":"robert_baratheon","x":452.64616416835213,"y":580.0810821018059},{"id":"loras_tyrell","x":871,"y":453},{"id":"rodrik_cassel","x":923,"y":564},{"id":"tywin_lannister","x":598.5928333332171,"y":434.60291089566886},{"id":"bran_stark","x":626.8815537162257,"y":201.05337580094934},{"id":"renly_baratheon","x":946,"y":612},{"id":"sansa_stark","x":605.8605861453174,"y":613.635821738573},{"id":"robert_arryn","x":1007,"y":490},{"id":"eddard_stark","x":482.44148601000967,"y":546.75408023963},{"id":"alliser_thorne","x":930,"y":339},{"id":"lysa_arryn","x":651.4691593909345,"y":646.7833590537875},{"id":"benjen_stark","x":964,"y":320},{"id":"stannis_baratheon","x":771.4542688592924,"y":405.58303150428384},{"id":"tommen_baratheon","x":784,"y":303},{"id":"gendry","x":660.3267479112609,"y":271.9125864083371},{"id":"margaery_tyrell","x":400.53096813032226,"y":446.246001088471},{"id":"roose_bolton","x":879,"y":488},{"id":"daario_naharis","x":698.6667589804052,"y":489.5583479121372},{"id":"osha","x":912,"y":269},{"id":"walder_frey","x":993,"y":369},{"id":"ramsay_bolton","x":756.0289012514381,"y":524.7576057524104},{"id":"luwin","x":560.6036984923456,"y":212.13573558629133},{"id":"hodor","x":703.5761728528659,"y":205.87240343399338},{"id":"tormund_giantsbane","x":807.1434726651938,"y":310.56785350560625},{"id":"jeor_mormont","x":727.3985732265897,"y":390.58203597392964},{"id":"aemon","x":680.8254070871562,"y":374.89059878563086},{"id":"syrio_forel","x":600.2112965067637,"y":263.7409825625326},{"id":"viserys_targaryen","x":867,"y":224},{"id":"drogo","x":731.2843456793665,"y":569.1613100568563},{"id":"samwell_tarly","x":638,"y":348},{"id":"old_nan","x":890,"y":378},{"id":"ilyn_payne","x":823,"y":462},{"id":"myrcella_baratheon","x":796,"y":290},{"id":"grey_worm","x":702.2032940957386,"y":608.1547394801664},{"id":"ygritte","x":719.7676805627889,"y":269.049435336411},{"id":"qotho","x":759,"y":557},{"id":"gregor_clegane","x":977,"y":303},{"id":"olenna_tyrell","x":876,"y":621}];
var initial_middle = {x: 0, y: 0, count: 0};
initial_configuration.forEach(function(n) {
  initial_middle.x += n.x;
  initial_middle.y += n.y;
  initial_middle.count += 1;
});
initial_middle.x /= initial_middle.count;
initial_middle.y /= initial_middle.count;
initial_middle.x -= 60;

var Network = function() {
  this.load = function(selector, data) {
    var network = this;
    this.dom_node = $(selector);
    this.width = this.dom_node.width() - 10;
    this.height = this.dom_node.height() - 10;
    this.image_id_map = {};

    d3.select(window).on('resize', function() {
      this.load(selector, data);
    }.bind(this));

    this.cutoff_slider = d3.slider()
      .min(0.01)
      .max(1)
      .value(0.45)
      .on("slide", function(evt, value) {
        d3.select("#cutoff-slider label .value").text((100 * value).toFixed(0) + ' %');
        this.update();
      }.bind(this));
    d3.select("#cutoff-slider label .value").text((100 * this.cutoff_slider.value()).toFixed(0) + ' %');
    d3.select("#cutoff-slider").call(this.cutoff_slider);

    this.charge_slider = d3.slider()
      .min(-10)
      .max(-500)
      .value(-85)
      .on("slide", function(evt, value) {
        d3.select("#charge-slider label .value").text(-value.toFixed(0));
        this.force_update();
      }.bind(this));
    d3.select("#charge-slider label .value").text(-this.charge_slider.value().toFixed(0));
    d3.select("#charge-slider").call(this.charge_slider);

    this.link_distance_slider = d3.slider()
      .min(10)
      .max(80)
      .value(40)
      .on("slide", function(evt, value) {
        d3.select("#link-distance-slider label .value").text(value.toFixed(0));
        this.force_update();
      }.bind(this));
    d3.select("#link-distance-slider label .value").text(this.link_distance_slider.value().toFixed(0));
    d3.select("#link-distance-slider").call(this.link_distance_slider);

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

    d3.select(selector + " svg").remove();
    this.svg = d3.select(selector).append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

    this.apply_filter = function(d) {
      if (d.hover || d.selected) {
        return "url(#glow)";
      }
    }

    function zoom() {
      if (d3.event.defaultPrevented) return;
      this.graph.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }

    this.node_double_click = function(d) {
      d3.event.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = false);
      network.force.resume();
    }

    this.scale_factor = this.height / 500;
    var zoom = d3.behavior.zoom()
      .scaleExtent([0.2, 8])
      .on("zoom", zoom.bind(this))
      .translate([(this.width - this.scale_factor * this.width) / 2,
                  (this.height - this.scale_factor * this.height) / 2])
      .scale(this.scale_factor);

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
      .attr("in", "SourceAlpha")
      .attr("dx", 10)
      .attr("dy", 10)
      .attr("result", "offsetOut");
    shadow_high.append("feGaussianBlur")
      .attr("in", "offsetOut")
      .attr("stdDeviation", 1)
      .attr("result", "blurOut");
    shadow_high.append("feColorMatrix")
      .attr("in", "blurOut")
      .attr("values", "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .5 0")
      .attr("result", "shadowOut");
    shadow_high.append("feBlend")
      .attr("in", "SourceGraphic")
      .attr("in2", "shadowOut")
      .attr("mode", "normal");

    var glow = this.defs.append("filter")
      .attr("id", "glow")
      .attr("x", "-100%")
      .attr("y", "-100%")
      .attr("width", "300%")
      .attr("height", "300%");
    glow.append("feColorMatrix")
      .attr("in", "SourceAlpha")
      .attr("type", "matrix")
      .attr("values", "0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0")
      .attr("result", "colorOut");
    glow.append("feGaussianBlur")
      .attr("in", "colorOut")
      .attr("result", "blurOut")
      .attr("stdDeviation", 10);
    glow.append("feBlend")
      .attr("in", "SourceGraphic")
      .attr("in2", "glowOut")
      .attr("mode", "normal");

    this.pattern_id = 1;

    this.graph = this.svg
      .append("g")
      .call(zoom)
      .append("g")
      .attr("transform",
            "translate(" + (this.width - this.scale_factor * this.width) / 2 + "," +
                           (this.height - this.scale_factor * this.height) / 2 + ")" +
            "scale(" + this.scale_factor + ")");

    this.banner_bar = this.svg.append("g");
    this.book_bar = this.svg.append("g");

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
        .gravity(GRAVITY)
        .charge(function(d) {
          if (d.intermediate) {
            return 0.2 * network.charge_slider.value();
          }
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

    if (this.force) {
      this.force.stop();
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
      if (d.intermediate) {
        return;
      }
      d3.event.sourceEvent.stopPropagation();
      d3.select(this).classed("fixed", d.fixed = true);
    }

    function dragend(d) {
      if (d.intermediate) {
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

    this.init_data(data);
    this.select_book(this.selected_book || 5);
  }

  this.add_image = function(path, aspect_ratio) {
    var cached = this.image_id_map[path];
    if (cached) {
      return cached;
    }

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

    this.image_id_map[path] = new_id;
    return new_id;
  }

  this.init_data = function(data) {
    // maintain node positions, so they can be restored when the data set
    // is swapped
    this.node_position = {};
    this.data = data;
    this.group_map = {};

    this.data.groups.data.groups.forEach(function(g) {
      this.group_map[g.id] = g;

      if (g.image) {
          var aspect_ratio = 1.5;
          if (g.shape == "circle") {
            aspect_ratio = 1;
          }
          g.image_id = this.add_image(BANNERS_PATH + g.image, aspect_ratio);
      }
    }.bind(this));

    this.visible_groups = this.data.groups.data.groups.filter(function(g) {
      return g.image;
    });

    this.data.books.forEach(function(b) {
      var aspect_ratio = 1.64;
      b.image_id = this.add_image(COVERS_PATH + b.image, aspect_ratio);
    }.bind(this));

    this.build_book_bar();
  }

  this.select_book = function(index) {
    this.selected_book = index;
    this.data.books.forEach(function(b, i) {
      b.selected = (i == index);
    });
    this.book_child.style("filter", this.apply_filter);
    this.load_data(this.data.books[index].data);
    this.update();
  }

  this.load_data = function(book_data) {
    if (this.all_nodes) {
      // if we are switching, first grab the positions of all nodes,
      // so we can restore it
      this.all_nodes.forEach(function(n) {
        this.node_position[n.id] = {x: n.x, y: n.y};
      }.bind(this));
    } else {
      initial_configuration.forEach(function(n) {
        this.node_position[n.id] = {
          x: this.width / 2 + (n.x - initial_middle.x) * 0.5,
          y: this.height / 2 + (n.y - initial_middle.y) * 0.5,
        };
      }.bind(this));
    }

    this.all_nodes = book_data.nodes.slice();
    this.all_edges = book_data.edges.slice();
    this.intermediate_nodes = [];
    this.node_map = {};

    for (var group_id in this.group_map) {
      this.group_map[group_id].edge_value_sum = 0;
    }

    this.all_nodes.forEach(function(n) {
      var old_position = this.node_position[n.id];
      if (old_position) {
        n.x = old_position.x;
        n.y = old_position.y;
        n.px = old_position.x;
        n.py = old_position.y;
      } else {
        var x, y;
        do {
          x = Math.random() * this.width - this.width / 2;
          y = Math.random() * this.height - this.height / 2;
        } while (x * x + y * y > this.height * this.height / 16);
        n.x = Math.floor(this.width / 2 + x);
        n.y = Math.floor(this.height / 2 + y);
        n.px = n.x;
        n.py = n.y;
      }
      n.radius = 15;
      n.weight = 1;

      if (n.image) {
          n.image_id = this.add_image(CHARACTERS_SMALL_PATH + n.image);
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
      function make_intermediate_id(source, target) {
        if (source.id < target.id) {
          return source.id + "-" + target.id;
        }
        return target.id + "-" + source.id;
      }
      var s = this.node_map[e.from],
          t = this.node_map[e.to],
          i = {id: make_intermediate_id(s, t),
               intermediate: true,
               node1: s,
               node2: t}; // intermediate node

      this.intermediate_nodes.push(i);

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

    this.all_nodes.forEach(function(n) {
      if (!n.group) {
        return;
      }

      var group = this.group_map[n.group];
      if (!group.edge_value_sum) {
        group.edge_value_sum = 0;
        if (!n.color) {
          n.color = group.color;
        }
      }

      group.edge_value_sum += n.edge_value_sum;
    }.bind(this));

    this.build_banner_bar();
    this.force_update();
  }

  this.build_book_bar = function() {
    if (this.book) {
      this.book.remove();
    }

    this.book = this.book_bar.selectAll("g.book")
        .data(this.data.books, function(d) { return d.id; });

    this.book_width = 30 * this.scale_factor;
    this.book_height = this.book_width * 1.64;
    this.book_space = 10 * this.scale_factor;
    this.book_bar_position = {
      x: this.width - this.book_width - this.book_space,
      y: this.height - this.data.books.length * (this.book_height + this.book_space),
    };

    this.book_parent = this.book.enter().append("g")
      .attr("id", function(d) { return "book_" + d.id; })
      .attr("class", "book")
      .style("filter", "url(#shadow-high)")
      .attr("transform", function(d, i) {
        var x = this.book_bar_position.x;
        var y = this.book_bar_position.y + i * (this.book_height + this.book_space);
        return "translate(" + x + "," + y + ")scale(" + (this.book_width / 100) + ")";
      }.bind(this));

    this.book_child = this.book_parent.append("g")
      .style("fill", function(d, i) {
          return 'url(#' + d.image_id + ')';
      })
      .style("filter", this.apply_filter)
      .on("mouseover", function(d) {
        d.hover = true;
        this.book_child.style("filter", this.apply_filter);
      }.bind(this))
      .on("mouseout", function(d) {
        d.hover = false;
        this.book_child.style("filter", this.apply_filter);
      }.bind(this))
      .on("click", function(d, i) {
        if (d.selected) {
          return;
        }
        this.select_book(i);
      }.bind(this));

    // inside the book box the width is 100, which is then scaled
    // to different resolutions
    this.book_child
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", 100)
      .attr("height", 100 * this.book_height / this.book_width);

    this.book.append("title")
      .text(function(d) { return d.title; });

    this.book.exit().remove();
  }

  this.build_banner_bar = function() {
    this.visible_groups.sort(function(a, b) {
      return b.edge_value_sum - a.edge_value_sum;
    });

    if (this.banner) {
      this.banner.remove();
    }

    this.banner = this.banner_bar.selectAll("g.banner")
        .data(this.visible_groups, function(d) { return d.id; });

    this.banner_width = 30 * this.scale_factor;
    this.banner_height = 45 * this.scale_factor;
    this.banner_space = 10 * this.scale_factor;
    this.banner_bar_position = {
      x: this.banner_space,
      y: this.height - ~~(this.visible_groups.length / 2) * (this.banner_height + this.banner_space),
    };

    this.banner_parent = this.banner.enter().append("g")
      .attr("id", function(d) { return "banner_" + d.id; })
      .attr("class", "banner")
      .style("filter", "url(#shadow-high)")
      .attr("transform", function(d, i) {
        var x = this.banner_bar_position.x + (i % 2) * (this.banner_width + this.banner_space);
        var y = this.banner_bar_position.y + ~~(i / 2) * (this.banner_height + this.banner_space);
        return "translate(" + x + "," + y + ")scale(" + (this.banner_width / 100) + ")";
      }.bind(this));

    this.banner_child = this.banner_parent.append("g")
      .style("fill", function(d, i) {
          return 'url(#' + d.image_id + ')';
      })
      .style("filter", this.apply_filter)
      .on("mouseover", function(d) {
        if (d.prevent_hover) {
          return;
        }
        d.hover = true;
        this.banner_child.style("filter", this.apply_filter);
      }.bind(this))
      .on("mouseout", function(d) {
        d.hover = false;
        d.prevent_hover = false;
        this.banner_child.style("filter", this.apply_filter);
      }.bind(this))
      .on("click", function(d) {
        d.selected = !d.selected;
        d.hover = d.selected;
        if (!d.selected) {
          // if we unselect a banner, then the flow should disappear,
          // but we also don't want it to reappear while the mouse is
          // still inside the element, so prevent_hover protects against
          // re-setting it... it is cleared on mouseout, restoring the
          // normal hover behaviour afterwards
          d.prevent_hover = true;
        } else {
          d.prevent_hover = false;
        }
        this.update();
      }.bind(this));

    this.banner_child
      .filter(function(d) { return d.shape == "shield" })
      .append("path")
      .attr("stroke-opacity", function(d) {
        if (d.id == "nights-watch" || d.id == "targaryen" || d.id == "freefolk" || d.id == "bolton") {
          return 0.3;
        }
        return 0;
      })
      .attr("stroke", "#888")
      .attr("d", "m 99.523233,0.06290596 c 0.26113,21.26875304 0.24596,42.53749304 0,63.80624304 -0.23922,20.48887 -1.0327,36.480561 -8.17061,48.980061 -8.598528,15.0601 -22.924919,25.9306 -41.351779,36.6105 -18.430237,-10.6799 -32.754939,-21.5482 -41.3534688,-36.6105 -7.139609,-12.5039 -7.93477203,-28.493351 -8.17062003,-48.980061 -0.245961,-21.26875 -0.261128,-42.53749 0,-63.80624304 z");

    // inside the banner box the width is 100, which is then scaled
    // to different resolutions, so here we need to use a radius of 50
    // and shift the center to (50, height / 2)
    this.banner_child
      .filter(function(d) { return d.shape == "circle" })
      .append("circle")
      .attr("cx", 50)
      .attr("cy", 50 * this.banner_height / this.banner_width)
      .attr("r", 50);

    this.banner.append("title")
      .text(function(d) { return d.name; });

    this.banner.exit().remove();
  }

  this.node_selected_by_group = function(n) {
    if (!n.groups) {
      return false;
    }

    var i;
    for (i = 0; i < n.groups.length; ++i) {
      if (this.group_map[n.groups[i]].selected) {
        return true;
      }
    }

    return false;
  }

  this.update = function() {
    var edges = [];
    var links = [];
    var linked_node_map = {};

    var selected_groups = this.visible_groups.filter(function(g) {
      return g.selected;
    });

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

      if (selected_groups.length) {
        if (!this.node_selected_by_group(s) ||
            !this.node_selected_by_group(t)) {
          return;
        }
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
        // we only care about linkedness when there aren't any groups selected,
        // in other words: a selected group counts as "linked"
        if (!selected_groups.length) {
          return;
        }
      }

      if (this.picture_nodes_only.property("checked") && !n.image) {
        return;
      }

      if (selected_groups.length) {
        if (n.intermediate) {
          if (!this.node_selected_by_group(n.node1) ||
              !this.node_selected_by_group(n.node2)) {
            return;
          }
        } else {
          if (!this.node_selected_by_group(n)) {
            return;
          }
        }
      }

      nodes.push(n);
    }.bind(this));

    this.force.links(links);

    if (this.link) {
      this.link.remove();
    }
    this.link = this.graph.selectAll("line.link")
      .data(edges, function(d) {
        if (d.source.id < d.target.id) {
          return d.source.id + "~" + d.target.id;
        }
        return d.target.id + "~" + d.source.id;
      });

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

function fetch_all_data(filename, callback) {
  jQuery.getJSON(DATA_PATH + filename, function(main_data) {
    var deferreds = [];
    deferreds.push(jQuery.getJSON(DATA_PATH + main_data.groups.path, function(data) {
      main_data.groups.data = data;
    }));

    var i;
    for (i = 0; i < main_data.books.length; ++i) {
      var book = main_data.books[i];
      deferreds.push(jQuery.getJSON(DATA_PATH + book.path, function(data) {
        this.data = data;
      }.bind(book)));
    }

    $.when.apply($, deferreds).then(function() {
      callback(main_data);
    });
  });
}

function load_dialogues(data_file, selector) {
  var network = new Network();
  document.network = network;

  fetch_all_data(data_file, function(data) {
    network.load(selector, data);
  });
}
