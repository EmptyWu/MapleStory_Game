
import pygetwindow as gw
import pyautogui
from PIL import Image
import pytesseract
import time

win = gw.getWindowsWithTitle('MapleStory Worlds-ChronoStory')[0]
print("win:", win)
x, y = win.left, win.top
print("x:", x,"y",y)

# 設定 Tesseract 路徑（Windows）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
win = gw.getWindowsWithTitle('MapleStory Worlds-ChronoStory')[0]
print("win:", win)
x, y = win.left, win.top
print("x:", x,"y",y,'width',win.width,'height',win.height)

def get_hp_percentage():
    location = pyautogui.locateOnScreen('MP.png', confidence=0.8)
    if location:
        region = (int(location.left), int(location.top), int(location.width), int(location.height))
        print('region:', region)

        mp_img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(mp_img)
        print('🧩 原始辨識結果:', text)
        try:
            current, total = map(int, text.strip().split('/'))
            print('current:',current,'total=',total)
            return current / total
        except Exception as e:
            print("OCR parsing error:", e)
            return None
    else:
        print("找不到 MP 圖示")

while True:
    print("Start")
    hp_ratio = get_hp_percentage()
    if hp_ratio is not None and hp_ratio < 0.3:
        #pyautogui.press('h')  # 假設 H 是喝水鍵
        print("HP 低於 30%，自動喝水！")
    time.sleep(1)
