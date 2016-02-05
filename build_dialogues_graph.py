#!/usr/bin/env python3
import json
import sys

if __name__ == '__main__':
    data = json.load(open(sys.argv[1]))

    colors = {
        "Stark": "#8c8",
        "Snow": "#9d9",
        "Lannister": "#c88",
        "Targaryen": "#ffd700",
        "Baratheon": "#88c",
        "Mormont": "#c84",
    }
    levels = {
        "Stark": 1,
        "Snow": 1,
        "Lannister": 2,
        "Targaryen": 3,
        "Baratheon": 4,
    }
    node_map = {}
    nodes = []
    edge_map = {}

    def get_node_id(speaker):
        if speaker.startswith('<'):
            return None

        if speaker not in node_map:
            new_id = len(nodes) + 1
            node = {"id": new_id, "title": speaker}
            house = speaker.split()[-1]
            if house in colors:
                node["color"] = colors[house]
                node["group"] = house

            node["level"] = levels.get(house, 0)

            nodes.append(node)
            node_map[speaker] = new_id

        return node_map[speaker]

    for speaker, value in data['dialogues'].items():
        speaker_id = get_node_id(speaker)
        if not speaker_id:
            continue

        for target, score in value.items():
            target_id = get_node_id(target)
            if not target_id:
                continue

            key = tuple(sorted([speaker_id, target_id]))
            edge_map[key] = edge_map.get(key, 0) + score

    max_score = max(edge_map.values())
    cutoff = max_score * 0.01

    edges = [{"from": k[0], "to": k[1], "value": v}
             for k, v in edge_map.items() if v >= cutoff]

    template = """<!doctype html>
<html>
<head>
  <title>Dialogues</title>

  <style type="text/css">
    body {
      font: 10pt arial;
    }
    #dialogues {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background-color:#333333;
    }
  </style>

  <script type="text/javascript" src="vis.min.js"></script>
  <link type="text/css" href="vis.min.css" rel="stylesheet"/>

  <script type="text/javascript">
    var nodes = null;
    var edges = null;
    var network = null;

    // Called when the Visualization API is loaded.
    function draw() {
      // create people.
      // value corresponds with the age of the person
      nodes = {nodes};

      // create connections between people
      // value corresponds with the amount of contact between two people
      edges = {edges};

      // create a network
      var container = document.getElementById('dialogues');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        nodes: {
          borderWidth:1,
          size:30,
          color: {
            border: '#222222',
            background: '#666666'
          },
          font:{color:'#eeeeee'}
        },
        edges: {
          color: 'lightgray'
        },
        layout: {
          improvedLayout: true
        },
        physics: {
          enabled: true,
          barnesHut: {
            springLength: 300,
            avoidOverlap: 0,
            gravitationalConstant: -5000,
            centralGravity: 0.5
          },
          repulsion: {
            nodeDistance: 150,
            centralGravity: 0.2
          },
          solver: "repulsion"
        }
      };
      network = new vis.Network(container, data, options);
    }
  </script>
</head>

<body onload="draw()">

<div id="dialogues"></div>
</body>
</html>
""".replace("{nodes}", json.dumps(nodes)).replace("{edges}", json.dumps(edges))

    open("html/dialogues.html", "w").write(template)
