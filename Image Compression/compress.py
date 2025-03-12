import os
from PIL import Image

# Define paths
input_folder = "filesToCompress"
output_folder = "output"
max_size_kb = 240  # Max file size in KB
max_size_bytes = max_size_kb * 1024  # Convert KB to bytes

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Function to compress images
def compress_image(input_path, output_path):
    with Image.open(input_path) as img:
        img_format = img.format  # Preserve original format
        img = img.convert("RGB") if img_format in ["JPEG", "JPG", "PNG"] else img

        # Initial quality setting
        quality = 85
        step = 5  # Step to reduce quality iteratively

        # Resize to reduce size while maintaining aspect ratio
        width, height = img.size
        while True:
            img.save(output_path, format="JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) <= max_size_bytes or quality < 10:
                break
            quality -= step

        print(f"Compressed {input_path} -> {output_path} | {os.path.getsize(output_path) / 1024:.2f} KB")

# Process all images in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        compress_image(input_path, output_path)

print("Compression complete. Check the 'output' folder.")
