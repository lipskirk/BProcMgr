import cv2
import os
import random
import skimage.exposure
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?', help="Path to input images")
parser.add_argument('-m','--masks', nargs='?', help="Path to masks")
parser.add_argument('-b','--backgrounds', nargs='?', help="Path to background images")
parser.add_argument('-o','--output', nargs='?', help="Path to where the final files will be saved")
args = parser.parse_args()

filenames = os.listdir(args.input)
backgrounds = os.listdir(args.backgrounds)
random.shuffle(backgrounds)
num_imgs = int(len(filenames))
num_backgrs = int(len(backgrounds))
if num_backgrs < num_imgs :
    num_diff = num_imgs - num_backgrs
    for n in range(num_diff) :
        backgrounds.append(random.choice(backgrounds))

cnt = 0
for file in filenames :
    if file.endswith(".jpg") :
        filename = file.split(".")
        image = cv2.imread(args.input + "/" + filename[0] + ".jpg")
        mask = cv2.imread(args.masks + "/" + filename[0] + ".png")
        backgr = cv2.imread(args.backgrounds + "/" + backgrounds[cnt])
        empty = cv2.imread("black.jpg")

        height, width, channels = backgr.shape
        if height < 640 :
                backgr = cv2.resize(backgr, (int(width*(640/height)), 640))
        height, width, channels = backgr.shape
        if width < 640 :
                backgr = cv2.resize(backgr, (640, int(height*(640/width))))
        height, width, channels = backgr.shape
        
        backgr = backgr[int((height/2)-320):int((height/2)+320), int((width/2)-320):int((width/2)+320)]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        (thresh, binRed) = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)

        b_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        b_mask = cv2.GaussianBlur(b_mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)
        b_mask = skimage.exposure.rescale_intensity(b_mask, in_range=(127.5, 255), out_range=(0, 255))

        backgr[b_mask > 0] = 0
        backgr += image * (b_mask > 0)

        gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        _,binary = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
        contours = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        cv2.drawContours(empty, contours, -1, (255, 255, 255), 2)

        b_cont = cv2.GaussianBlur(empty, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)

        gr_cont = cv2.cvtColor(b_cont, cv2.COLOR_BGR2GRAY)
        _,bin_cont = cv2.threshold(gr_cont, 100, 255, cv2.THRESH_BINARY)
        output = cv2.inpaint(backgr, bin_cont, 3, cv2.INPAINT_NS)

        cv2.imwrite(args.output + "/" + filename[0] + "_RB" + ".jpg", output)
        cnt += 1
        print("Replaced background in " + str(cnt) + "/" + str(num_imgs))
print("Done")

