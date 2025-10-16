import cv2
import easyocr
import re

# 初始化 EasyOCR（只需一次）
_reader = easyocr.Reader(['en'], gpu=False)

def get_mp_from_image(path: str,name:str):
    """
    從圖片檔案讀取 MP 數值，並回傳比值 (current / total)
    範例輸出: 0.45 表示 45%
    """
    img = cv2.imread(path)
    if img is None:
        print(f"❌ 無法開啟檔案: {path}")
        return None

    # OCR 辨識
    results = _reader.readtext(img, detail=0)
    text = " ".join(results)
    print("🧩 EasyOCR 辨識結果:", repr(text))

    # 清理雜訊字元
    text = text.replace(',', '')
    text = re.sub(r'[^0-9/ ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # 嘗試找出 "數字/數字" 格式
    m = re.search(r'(\d{2,5})\s*/\s*(\d{2,5})', text)
    if not m:
        # 若沒斜線，但有兩組數字，就自動當成 "current total"
        nums = re.findall(r'\d{2,5}', text)
        if len(nums) >= 2:
            m = [nums[0], nums[1]]
            cur, tot = map(int, m)
        else:
            print("❌ 未找到足夠的數字。")
            return None
    else:
        cur, tot = map(int, m.groups())

    # 邏輯修正：避免錯誤順序
    if cur > tot:
        cur, tot = tot, cur

    ratio = cur / tot if tot else 0
    print(f"🎯 {name} 數值: {cur}/{tot} ({ratio*100:.1f}%)")
    return ratio
