import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?', default="labels.json",help="Path to the input JSON file")
parser.add_argument('-o','--output', nargs='?', default="predictions.json", help="Path to the output JSON file")
args = parser.parse_args()

with open(args.input, 'r') as input_file:
    data_input = json.load(input_file)

image_ids = []
image_ids.append(0)
for image in data_input["images"]:
    filename = image["file_name"]
    name = filename.lstrip('0')
    name = name.strip('.jpg')
    image_ids.append(int(name))

for annotation in data_input["annotations"]:
    annotation.pop("id")
    annotation.pop("area")
    annotation.pop("iscrowd")
    annotation["bbox"]=[
        round(annotation["bbox"][0],2),
        round(annotation["bbox"][1],2),
        round(annotation["bbox"][2],2),
        round(annotation["bbox"][3],2)]
    annotation["score"] = round(annotation["score"],3)
    annotation["image_id"] = image_ids[annotation["image_id"]]

with open(args.output, 'w') as output_file:
    json.dump(data_input["annotations"], output_file, indent=2)
