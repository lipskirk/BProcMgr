import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t','--train', nargs='?', default="train/labels.json", help="Path to the train split JSON file")
parser.add_argument('-v','--validation', nargs='?', default="validation/labels.json", help="Path to the validation split JSON file")
parser.add_argument('-e','--test', nargs='?', default="test/image_info_test-dev2017.json", help="Path to the test split JSON file")
parser.add_argument('-c','--categories', nargs='?', default="coco_categories.txt", help="Path to .txt file with COCO categories")
args = parser.parse_args()

with open(args.categories, 'r') as file:
    coco_labels = file.read().splitlines()

def fix_categories(filename, include_background) :
    if include_background :
        skip_bg = False
    else :
        skip_bg = True
        
    with open(filename, 'r') as labels_input:
        data_input = json.load(labels_input)

    json_categories = []
    id_count = -1
    for label in coco_labels :
        id_count += 1
        if skip_bg :
            skip_bg = False
        else :
            json_categories.append(
                {
                    "id" : id_count,
                    "supercategory" : label.split(':')[1],
                    "name" : label.split(':')[0]
                })

    if "categories" in data_input :
       data_input["categories"] = json_categories

    if "info" in data_input :
        if "categories" in data_input["info"] :
            data_input["info"]["categories"] = json_categories
            

    with open(filename, 'w') as output_file:
        json.dump(data_input, output_file)

fix_categories(args.train, True)
fix_categories(args.validation, True)
fix_categories(args.test, False)
