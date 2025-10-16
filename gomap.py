#MapleStory Worlds-ChronoStory
import pygetwindow as gw
import pyautogui
import pytesseract
import re
from PIL import Image, ImageEnhance, ImageFilter
import time

# ====== Tesseract OCR 設定 ======
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ====== 取得 ChronoStory 視窗位置 ======
win = gw.getWindowsWithTitle('MapleStory Worlds-ChronoStory')[0]
print("win:", win)
x, y = win.left, win.top
print("x:", x,"y",y,'width',win.width,'height',win.height)

# ====== 在畫面上尋找 MP 標示區域 ======
location = pyautogui.locateOnScreen('MP.png', confidence=0.7)
def get_hp_percentage():
    if location:
        region = (int(location.left), int(location.top), int(location.width), int(location.height))
        print('region:', region)

        # 確保 region 是四個整數
        if all(isinstance(i, int) for i in region):
            mp_img = pyautogui.screenshot(region=region)
            mp_img.save("mp_capture.png")  # 可選：儲存擷取畫面
            
            print("✅ 成功擷取 MP 區域，開始 OCR 解析...")

            # ====== 前處理影像 ======
            img = mp_img.convert("L")  # 灰階
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # 增加對比
            img = img.point(lambda x: 0 if x < 140 else 255)  # 二值化
            #img = img.crop((10, 0, img.width - 5, img.height))  # 從左切掉10px避免多抓符號
            img = img.filter(ImageFilter.SHARPEN)  # 銳化

            # ====== OCR 辨識 ======
            tess_config = r'-c tessedit_char_whitelist=0123456789/, -l eng --psm 7'
            text = pytesseract.image_to_string(img,config=tess_config)
            print("🧩 原始辨識結果1:", repr(text))
            #text = text.replace('\n', ' ')           
            text = text.strip().replace('\n', ' ')
            text = re.sub(r'[^0-9/,]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            print("🧩 原始辨識結果2:", repr(text))

            # === 🧩 新增：防止 ] 被辨識為尾巴的 "1" ===
            # 例如 '433/1,5071' → '433/1,507'
            m = re.match(r'(\d{2,6})/(\d{1,3},?\d{3})1$', text)
            if m:
                text = f"{m.group(1)}/{m.group(2)}"
                print(text)
            
            # 偵測開頭多餘 1 的情況（例如 1593 → 593, 1208 → 208）
            # 規則：如果開頭是 1，且該數值 > 後方總值
            m = re.match(r'1+(\d{3,4})/(\d{1,2},?\d{3})', text)
            if m:
                left_raw = m.group(1)
                right_val = int(m.group(2).replace(',', ''))
                left_val = int(left_raw)
                if left_val < right_val or text.startswith('11'):  # 合理修正
                    print(f"🔧 修正開頭多餘 '1': {text} → ", end="")
                    text = f"{m.group(1)}/{m.group(2)}"
                    print(text)

            print("🧩 原始辨識結果3:", repr(text))
            # ====== 用正則提取數字 ======
            pattern = r'\d{1,3}(?:,\d{3})*'
            nums = re.findall(pattern, text)
            if len(nums) >= 2:
                current = int(nums[0].replace(',', ''))
                total   = int(nums[1].replace(',', ''))
                #if current > total and len(nums) >= 2:
                    # 嘗試交換一次
                #    current, total = total, current
                ratio = current / total if total else 0.0
                print(f"🎯 MP 數值: {current}/{total} ({ratio*100:.1f}%)")
                return current / total
            else:
                print("❌ 無法解析出數字，原始文字:", text)
                return None
        else:
            print("region 格式錯誤")
            return None
    else:
        print("找不到 MP 圖示或不在視窗範圍內")
        return None

while True:
    print("Start")
    hp_ratio = get_hp_percentage()    
    if hp_ratio is not None and hp_ratio < 0.2:
        #pyautogui.press('insert')  # 假設 H 是喝水鍵
        print("HP 低於 20%，自動喝水！")
    time.sleep(3)
