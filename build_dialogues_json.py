#!/usr/bin/env python3
import argparse
import json
import os

IMAGE_DIR = "pics/small"
BANNER_DIR = "banners"

IGNORED_NODES = {
    "<unknown>",
    "<narrarow>",
    "Stark",
    "Targaryen",
    "Lady",
    "Rhaegar Targaryen",
}

GROUP_ASSOCIATIONS = {
    "Joffrey Baratheon": ["baratheon", "lannister"],
    "Tommen Baratheon": ["baratheon", "lannister"],
    "Catelyn Stark": ["stark", "tully"],
    "Maester Aemon": ["nights-watch", "targaryen"],
    "Jon Snow": ["nights-watch", "stark"],
    "Samwell Tarly": ["nights-watch", "tarly"],
    "Jeor Mormont": ["nights-watch", "mormont"],
    "Benjen Stark": ["nights-watch", "stark"],
    "Bowen Marsh": ["nights-watch"],
    "Alliser Thorne": ["nights-watch"],
    "Daenerys Targaryen": ["dothraki", "targaryen"],
    "Drogo": ["dothraki"],
    "Qotho": ["dothraki"],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=float, default=0.05)
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    data = json.load(open(args.input))

    colors = {
        "stark": "#8c8",
        "lannister": "#d22",
        "targaryen": "#b80",
        "dothraki": "#f80",
        "baratheon": "#ffd700",
        "mormont": "#fff",
        "tully": "#88c",
        "arryn": "#55a",
        "greyjoy": "#777",
        "frey": "#555",
        "tarly": "#2f2",
        "nights-watch": "#000",
    }

    groups = []
    for group in colors:
        if group == "dothraki":
            name = "Dothraki"
        elif group == "nights-watch":
            name = "Night's Watch"
        else:
            name = "House " + group.capitalize(),

        group_data = {
            "id": group,
            "name": name,
            "color": colors[group],
        }

        banner_img = os.path.join(BANNER_DIR, group + ".jpg")
        if os.path.exists("html/" + banner_img):
            group_data["image"] = banner_img

        if group == "dothraki":
            group_data["shape"] = "circle"
        else:
            group_data["shape"] = "shield"

        groups.append(group_data)

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
                "name": speaker,
            }
            group = speaker.split()[-1].lower()
            groups = []
            if speaker in GROUP_ASSOCIATIONS:
                groups = GROUP_ASSOCIATIONS[speaker]
            elif group in colors:
                groups.append(group)

            if groups:
                node["groups"] = groups
                node["group"] = groups[0]
                node["color"] = colors[groups[0]]

            img = os.path.join(IMAGE_DIR, speaker + ".jpg")
            if os.path.exists("html/" + img):
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

    edges = [{"from": k[0], "to": k[1], "value": v}
             for k, v in edge_map.items()]

    json.dump({'nodes': nodes, 'edges': edges, 'groups': groups},
              open(args.output, "w"))
