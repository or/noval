#!/usr/bin/env python3
import argparse
import json
import os
import re

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
    "Aemon": ["nights-watch", "targaryen"],
    "Jon Snow": ["nights-watch", "stark", "freefolk"],
    "Samwell Tarly": ["nights-watch", "tarly"],
    "Jeor Mormont": ["nights-watch", "mormont"],
    "Benjen Stark": ["nights-watch", "stark"],
    "Bowen Marsh": ["nights-watch"],
    "Alliser Thorne": ["nights-watch"],
    "Daenerys Targaryen": ["dothraki", "targaryen"],
    "Drogo": ["dothraki"],
    "Qotho": ["dothraki"],
    "Grey Worm": ["unsullied"],
    "Ygritte": ["freefolk"],
    "Tormund Giantsbane": ["freefolk"],
    "Mance Rayder": ["freefolk"],
    "Osha": ["freefolk"],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=float, default=0.05)
    parser.add_argument("--groups")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    if args.groups:
        known_groups = {x["id"]: x for x in json.load(open(args.groups))["groups"]}
    else:
        print("warning: no groups file specified")
        known_groups = {}

    data = json.load(open(args.input))

    node_map = {}
    nodes = []
    edge_map = {}

    def name_to_id(name):
        return re.sub(r'[^a-z_]', '', name.lower().replace(' ', '_'))

    def get_node_id(speaker):
        if speaker in IGNORED_NODES:
            return None

        if speaker not in node_map:
            new_id = name_to_id(speaker)
            node = {
                "id": new_id,
                "name": speaker,
            }
            group = speaker.split()[-1].lower()
            groups = []
            if speaker in GROUP_ASSOCIATIONS:
                groups = GROUP_ASSOCIATIONS[speaker]
            elif group in known_groups:
                groups.append(group)

            if groups:
                node["groups"] = groups
                node["group"] = groups[0]
                node["color"] = known_groups[groups[0]]["color"]

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

    json.dump({'nodes': nodes, 'edges': edges},
              open(args.output, "w"))
