
import base64, io
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import numpy as np
from scipy.ndimage import uniform_filter

def solve_image_captcha():
    try:
        img_src = "data:image/png;base64,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"

        if img_src.startswith('data:image'):
            # Decode base64
            img_base64 = img_src.split(',')[1]
            img_bytes = base64.b64decode(img_base64)
            pil_image = Image.open(io.BytesIO(img_bytes)).convert("L")

            # Crop small margins (5%)
            w, h = pil_image.size
            margin = int(w * 0.05)
            pil_image = pil_image.crop((margin, 0, w - margin, h))

            # Enhance contrast
            pil_image = ImageOps.autocontrast(pil_image)

            # Convert to numpy
            arr = np.array(pil_image)

            local_mean = uniform_filter(arr.astype(float), size=15)
            bin_arr = np.where(arr < local_mean - 10, 0, 255).astype(np.uint8)

            bin_img = Image.fromarray(bin_arr)

            # Remove tiny dots/lines using median filter
            bin_img = bin_img.filter(ImageFilter.MedianFilter(3))

            # OCR
            config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            captcha_text = pytesseract.image_to_string(bin_img, config=config).strip()

            # Keep only alphanumeric
            captcha_text = ''.join([c for c in captcha_text if c.isalnum()])

            # Force exactly 6 characters
            if len(captcha_text) > 6:
                start_idx = (len(captcha_text) - 6) // 2
                captcha_text = captcha_text[start_idx:start_idx + 6]
            elif len(captcha_text) < 6:
                captcha_text = captcha_text.ljust(6, 'X')

            print(f"[OCR Result] Captcha detected: '{captcha_text}'")

            # Debug
            bin_img.save("debug_bin.png")
            pil_image.save("debug_cropped.png")

    except Exception as e:
        print("No image captcha on this page.", e)

solve_image_captcha()
