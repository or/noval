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
            if os.path.exists("html/" + img):
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
            return "definite"

        if "image" in speaker_node and "image" in target_node:
            cutoff = max_score * args.cutoff / 2

        cutoff = max_score * args.cutoff
        if value >= cutoff:
            return "ok"
        else:
            return "cutoff"

    for n1, n2 in DEFINITE_EDGES:
        id1 = node_map[n1]
        id2 = node_map[n2]
        key = tuple(sorted([id1, id2]))
        edge_map[key] = 1

    edges = [{"from": k[0], "to": k[1], "value": v, "flag": edge_counts(k[0], k[1], v)}
             for k, v in edge_map.items()]

    json.dump({'nodes': nodes, 'edges': edges}, open(args.output, "w"))
