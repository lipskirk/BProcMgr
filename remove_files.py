import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?', help="Path to input images")
parser.add_argument('-r','--removes', nargs='?', help="Path to masks")
args = parser.parse_args()

input_files = os.listdir(args.input)
remove_files = os.listdir(args.removes)

f_num = int(len(input_files))
cnt = 0
for file in input_files :
    cnt += 1
    print("Check file " + str(cnt) + "/" + str(f_num))
    if file in remove_files :
        os.remove(args.input + "/" + file)
        print("Removed file " + file)
