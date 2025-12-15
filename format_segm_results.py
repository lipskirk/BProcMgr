import blenderproc as bproc
import json
import argparse
import numpy
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?', help="Path to the input JSON file")
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

ann_num = len(data_input["annotations"])
cnt = 0
for annotation in data_input["annotations"]:

    width = data_input["images"][annotation["image_id"]-1]["width"]
    height = data_input["images"][annotation["image_id"]-1]["height"]

    img = Image.new('L', (width, height), 0)
    for polygon in annotation["segmentation"] :
        ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(img)
    annotation["segmentation"] = bproc.python.writer.CocoWriterUtility.binary_mask_to_rle(mask)
    
    annotation.pop("id")
    annotation.pop("area")
    annotation.pop("iscrowd")
    annotation.pop("bbox")
    annotation["score"] = round(annotation["score"],3)
    annotation["image_id"] = image_ids[annotation["image_id"]]

    cnt += 1
    print("Converted " + str(cnt) + "/" + str(ann_num) + " from polygon to RLE")

with open(args.output, 'w') as output_file:
    json.dump(data_input["annotations"], output_file, indent=2)
