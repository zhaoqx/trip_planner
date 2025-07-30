from PIL import Image
import os

def convert_png_to_jpg(png_path, jpg_path):
    """Converts a PNG image to JPG."""
    if not os.path.exists(png_path):
        print(f"错误：找不到源文件 {png_path}")
        return

    try:
        with Image.open(png_path) as img:
            # Convert to RGB if it has an alpha channel (transparency)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(jpg_path, "jpeg")
        print(f"成功将 {png_path} 转换为 {jpg_path}")
    except Exception as e:
        print(f"转换图片时出错: {e}")

if __name__ == "__main__":
    png_file = os.path.join("materials", "map_day1.png")
    jpg_file = os.path.join("materials", "map_day1.jpg")
    convert_png_to_jpg(png_file, jpg_file)
