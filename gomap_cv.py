from ocr_reader import get_mp_from_image

# 擷取 MP 區域
#mp_img = pyautogui.screenshot(region=region)
#mp_img.save("mp_capture.png")

# 使用 EasyOCR 模組辨識
ratio = get_mp_from_image("mp_capture.png")

if ratio is not None and ratio < 0.2:
    #pyautogui.press('insert')
    print("🧃 MP 低於 20%，自動喝水！")