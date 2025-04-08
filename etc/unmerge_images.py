from PIL import Image
from pathlib import Path

def unmerge_images(input_image_path, output_folder, num_parts):
    merged_image = Image.open(input_image_path)
    width, height = merged_image.size
    part_height = height // num_parts
    
    for i in range(num_parts):
        box = (0, i * part_height, width, (i + 1) * part_height)
        part_image = merged_image.crop(box)
        part_image.save(f"{output_folder}/part_{i + 1}.png")

input_image_path = "./concat_v.png"  
output_folder = Path("out")
output_folder.mkdir(exist_ok=True)
num_parts = 66

unmerge_images(input_image_path, output_folder, num_parts)
