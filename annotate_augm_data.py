import os
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?',  help="Path to input .txt labels directory")
parser.add_argument('-o','--output', nargs='?', help="Path to output .txt labels directory")
parser.add_argument('-a','--augm_imgs', nargs='?', help="Path to augmented images to annotate")
args = parser.parse_args()

cnt = 0
num_imgs = len(os.listdir(args.augm_imgs))
for image in os.listdir(args.augm_imgs) :
    if image.endswith(".jpg") :
        cnt += 1
        img_name = image.split(".")
        txt_name = img_name[0].split("_")
        input_txt = txt_name[0] + ".txt"
        output_txt = img_name[0] + ".txt"
        shutil.copyfile(os.path.join(args.input,input_txt), os.path.join(args.output,output_txt))
        print("Annotated image " + image + " : " +  str(cnt) + "/" + str(num_imgs))

