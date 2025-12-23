from PIL import Image
import os

sizes = [16, 48, 128]
# The user might have meant the generated icon was 1024, but saved as icon128.png?
# Let's check the size or just resize whatever is there.
# If the user says "Expected icon at icons/icon128.png to be 128 pixels wide but was 1024", 
# it means the file named icon128.png is actually 1024px.
src = "/mnt/shared_data/projects/v2/extension/icons/icon128.png"

try:
    with Image.open(src) as img:
        for size in sizes:
            out = f"/mnt/shared_data/projects/v2/extension/icons/icon{size}.png"
            img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
            img_resized.save(out)
            print(f"Resized to {size}x{size}: {out}")
except Exception as e:
    print(f"Error: {e}")
