from PIL import Image
import os

def preprocess_image(img_path, out_path, box_w, box_h):
    """
    Resize and pad the image to fit exactly into the target box (box_w x box_h, in pixels),
    preserving aspect ratio and filling extra space with white.
    """
    try:
        img = Image.open(img_path)
        img = img.convert('RGB')
        img_w, img_h = img.size
        # Calculate scale to fit box
        scale_w = box_w / img_w
        scale_h = box_h / img_h
        scale = min(scale_w, scale_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        # 兼容不同 Pillow 版本的缩放算法
        resample = None
        # Pillow >= 9.1.0 推荐用 Image.Resampling.LANCZOS
        if hasattr(Image, 'Resampling'):
            resample = getattr(Image.Resampling, 'LANCZOS', None)
        # Pillow < 9.1.0 用 Image.LANCZOS
        if resample is None and hasattr(Image, 'LANCZOS'):
            resample = getattr(Image, 'LANCZOS', None)
        # Pillow 低版本用 Image.BICUBIC
        if resample is None and hasattr(Image, 'BICUBIC'):
            resample = getattr(Image, 'BICUBIC', None)
        # 如果都没有，降级为None（Pillow会用默认算法）
        if resample is None:
            resample = None
        img_resized = img.resize((new_w, new_h), resample)
        # Create white background
        background = Image.new('RGB', (box_w, box_h), (255, 255, 255))
        # Center the image
        x = (box_w - new_w) // 2
        y = (box_h - new_h) // 2
        background.paste(img_resized, (x, y))
        background.save(out_path, 'JPEG')
        print(f"已处理图片: {out_path}")
    except Exception as e:
        print(f"处理图片 {img_path} 时出错: {e}")

def main():
    # PDF中预留区域的像素尺寸（letter纸张，1英寸=72像素）
    box_w = int(8.5 * 72 - 1 * 72)  # width - 1 inch
    box_h = int(3 * 72)             # 3 inch height
    materials_dir = os.path.dirname(__file__)
    for i in range(1, 9):
        img_path = os.path.join(materials_dir, f"map_day{i}.jpg")
        if os.path.exists(img_path):
            preprocess_image(img_path, img_path, box_w, box_h)

if __name__ == "__main__":
    main()
