from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import torch
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', nargs='?', help="Path to input images")
parser.add_argument('-m','--masks', nargs='?', help="Path to masks")
parser.add_argument('-o','--output', nargs='?', help="Path to output")
parser.add_argument('-n','--num_output_imgs', nargs='?', type = int, default=1, help="Number of output images per one input image")
parser.add_argument('-s','--strength', nargs='?', type = float, default=0.2, help="Strength, fraction of inference steps")
parser.add_argument('-g','--guidance_scale', nargs='?', type = float, default=3.0, help="Guidance scale")
parser.add_argument('-p','--inference_steps', nargs='?', type = int, default=50, help="Number of inference steps")
args = parser.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", device)

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-inpainting",
    dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

prompt = (
    "the same scene with more realistic [DETECTED_OBJECT], "
    "[DETECTED_OBJECT] is always banana or apple or orange or carrot, "
    "realistic colors, visible imperfections, "
    "{fresh|ripe|decayed}, "
    "random variety of [DETECTED_OBJECT], "
    "realistic lighting and natural, detailed texture, "
    "((realistic imperfections)) based on [DETECTED_OBJECT] type, "
)

negative_prompt = (
    "extra [DETECTED_OBJECT], extra objects, "
    "moved objects, removed objects, "
    "painting, drawing, cartoon, abstract, text, logo, watermark, "
    "blur, smudge, "
)

filenames = os.listdir(args.input)
f_num = str(int(len(filenames)))
cnt = 0
for file in filenames :
  if file.endswith(".jpg") :
    cnt += 1
    print(str(cnt) + "/" + f_num)
    filename = file.split(".")
    image = Image.open(args.input + "/" + filename[0] + ".jpg").convert("RGB")
    mask  = Image.open(args.masks + "/" + filename[0] + ".png").convert("L")
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=image,
        mask_image=mask,
	strength=args.strength,
        guidance_scale=args.guidance_scale,
        num_inference_steps=args.inference_steps,
        num_images_per_prompt=args.num_output_imgs,
      ).images
    n = 0
    for img in result :
      img.save(args.output + "/" + filename[0] + "_" + str(n) + ".jpg")
      n += 1
