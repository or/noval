#!/usr/bin/env python3
import argparse
import json
import os

IMAGE_DIR = "pics/small"
DEFINITE_EDGES = [
    ('Brandon Stark', 'Hodor'),
    ('Robb Stark', 'Roose Bolton'),
    ('Lysa Arryn', 'Robert Arryn'),
    ('Cersei Lannister', 'Robert Baratheon'),
]
IGNORED_NODES = {
    "<unknown>",
    "<narrarow>",
    "Stark",
    "Targaryen",
    "Lady",
    "Rhaegar Targaryen",
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=float, default=0.05)
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    data = json.load(open(args.input))

    colors = {
        "Stark": "#8c8",
        "Snow": "#9d9",
        "Lannister": "#d22",
        "Targaryen": "#b80",
        "Aemon": "#b80",
        "Baratheon": "#ffd700",
        "Mormont": "#fff",
        "Tully": "#88c",
        "Arryn": "#55a",
        "Greyjoy": "#777",
        "Tarly": "#2f2",
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
        if speaker in IGNORED_NODES:
            return None

        if speaker not in node_map:
            new_id = len(nodes) + 1
            node = {
                "id": new_id,
                "title": speaker,
                "shadow": {
                    "enabled": True,
                    "size": 20,
                    "x": 10,
                    "y": 10,
                }
            }
            house = speaker.split()[-1]
            if house in colors:
                node["color"] = colors[house]
                node["group"] = house

            node["level"] = levels.get(house, 0)
            img = os.path.join(IMAGE_DIR, speaker + ".jpg")
            if os.path.exists(img):
                node["shape"] = "circularImage"
                node["image"] = img

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

    def edge_counts(speaker_id, target_id, value):
        speaker_node = nodes[speaker_id - 1]
        target_node = nodes[target_id - 1]
        if tuple(sorted([speaker_node['title'], target_node['title']])) in DEFINITE_EDGES:
            return True

        if "image" in speaker_node and "image" in target_node:
            cutoff = max_score * args.cutoff / 2

        cutoff = max_score * args.cutoff
        return value >= cutoff

    for n1, n2 in DEFINITE_EDGES:
        id1 = node_map[n1]
        id2 = node_map[n2]
        key = tuple(sorted([id1, id2]))
        edge_map[key] = 1

    edges = [{"from": k[0], "to": k[1], "value": v}
             for k, v in edge_map.items() if edge_counts(k[0], k[1], v)]

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
          borderWidth:5,
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
          randomSeed: 2107,
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

    open(args.output, "w").write(template)
