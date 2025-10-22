import cv2
import easyocr
import re
from src.utils.logger import logger

# 初始化 EasyOCR（只需一次）
_reader = easyocr.Reader(['en'], gpu=False)


def preprocess(img):
    """將圖片灰階化 + 放大 + 二值化，提昇 EasyOCR 準確率"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # 放大
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)  # 提高對比
    return thresh

def parse_hp_text(text: str):
    """清理並解析出 cur / tot 數字（不交換順序）"""
    # 1️⃣ 標點與格式修正
    t = text.replace('.', ',')
    t = re.sub(r',+', ',', t)  # 合併多個逗號
    t = re.sub(r'(?<=\d)\s+(?=\d)', '', t)  # 移除數字中間空白

    # 2️⃣ 優先擷取兩組數字（允許千分位）
    num_pat = re.compile(r'\d{1,3}(?:,\d{3})+|\d{3,5}')
    nums = num_pat.findall(t)
    if len(nums) < 2:
        nums = re.findall(r'\d+', t)
    if len(nums) < 2:
        return None

    # 3️⃣ 轉為整數
    def to_int(s: str) -> int:
        return int(s.replace(',', ''))

    cur, tot = to_int(nums[0]), to_int(nums[1])

    # 4️⃣ 容錯處理：不交換，只補漏位
    if cur > tot:
        logger.warning(f"⚠️ OCR 可能誤讀：cur({cur}) > tot({tot})，請檢查影像或辨識結果")

        # 若 total 只有 3 位且 cur 開頭是 1，推測漏掉 '1'
        if len(str(tot)) == 3 and str(cur).startswith('1'):
            tot = int('1' + str(tot))
            logger.info(f"🩹 自動補位 total → {tot}")

    return cur, tot

def get_mp_from_image(path: str,name:str):
    """
    從圖片檔案讀取 MP 數值，並回傳比值 (current / total)
    範例輸出: 0.45 表示 45%
    """
    img = cv2.imread(path)
    if img is None:
        logger.info(f"❌ 無法開啟檔案: {path}")
        return None

    # OCR 辨識
    proc = preprocess(img)
    results = _reader.readtext(proc, detail=0)
    text = " ".join(results)
    logger.info(f"🧩 EasyOCR 辨識結果:{repr(text)}")

    parsed = parse_hp_text(text)

    if not parsed:
        logger.info("❌ 未找到有效的數字格式")
        return None

    cur, tot = parsed
    ratio = cur / tot if tot else 0

    logger.info(f"🎯 {name} 數值: {cur}/{tot} ({ratio*100:.1f}%)")
    return ratio
