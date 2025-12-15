import json
import yaml
import os
import shutil
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input_path', nargs='?', help="Input set path")
parser.add_argument('-o','--output_path', nargs='?', help="Output subset path")
parser.add_argument('-n','--number_imgs', nargs='?', help="Number of images in output subset")
args = parser.parse_args()

if not os.path.exists(args.output_path) :
    os.makedirs(args.output_path)

with open(os.path.join(args.input_path, "dataset.yaml"), 'r') as f:
    yaml_file = yaml.safe_load(f)
yaml_file["path"] = args.output_path
with open(os.path.join(args.output_path, "dataset.yaml"), 'w') as f:
    yaml.dump(yaml_file, f)

if not os.path.exists(os.path.join(args.output_path, "images")) :
    os.makedirs(os.path.join(args.output_path, "images"))
if not os.path.exists(os.path.join(args.output_path, "labels")) :
    os.makedirs(os.path.join(args.output_path, "labels"))

if not os.path.exists(os.path.join(args.output_path, "images", "val")) :
    shutil.copytree(os.path.join(args.input_path, "images", "val"), os.path.join(args.output_path, "images", "val"))
if not os.path.exists(os.path.join(args.output_path, "labels", "val")) :
    shutil.copytree(os.path.join(args.input_path, "labels", "val"), os.path.join(args.output_path, "labels", "val"))

if not os.path.exists(os.path.join(args.output_path, "images", "train")) :
    os.makedirs(os.path.join(args.output_path, "images", "train"))
if not os.path.exists(os.path.join(args.output_path, "labels", "train")) :
    os.makedirs(os.path.join(args.output_path, "labels", "train"))

DIR = os.path.join(args.input_path, "images", "train")
filenames = [f for f in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, f))]

subset = random.sample(filenames, int(args.number_imgs))
for file_jpg in subset :
    shutil.copyfile(os.path.join(args.input_path, "images", "train", file_jpg), os.path.join(args.output_path, "images", "train", file_jpg))
    file = file_jpg.split('.')
    file_txt = file[0] + ".txt"
    if os.path.isfile(os.path.join(args.input_path, "labels", "train", file_txt)) :
        shutil.copyfile(os.path.join(args.input_path, "labels", "train", file_txt), os.path.join(args.output_path, "labels", "train", file_txt))
