import pyautogui
import os
import time
from src.utils.logger import logger
import cv2
import numpy as np
#import win32gui

# ====== 在畫面上尋找工具列位置 ======
# 增加傳入參數，代表辨識兩次的圖片
def GetImgLocation(image1, image2):
    '''
    在畫面上尋找工具列位置
    '''
    tool1_location = None
    logger.info(f"圖片名稱: {image1}")
    try:
        tool1_location = pyautogui.locateOnScreen(image1, confidence=0.7)
    except pyautogui.ImageNotFoundException:
        try:
            tool1_location = pyautogui.locateOnScreen(image2, confidence=0.7)
        except pyautogui.ImageNotFoundException:
            tool1_location = None
    logger.info(f"GetImgLocation位置: {tool1_location}")
    return tool1_location

def find_images_in_folder(confidence=0.7):
    """
    掃描資料夾內所有圖片，檢查是否出現在螢幕畫面中。
    若有找到，回傳檔名與位置。
    """
    folder_path = os.path.join(os.getcwd(), "minmaps")  # 自動抓當前路徑下的 minmaps 資料夾
    logger.info(f"資料夾: {folder_path}")
    if not os.path.exists(folder_path):
        logger.info(f"❌ 找不到資料夾: {folder_path}")
   
    
    # 掃描所有圖片
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png')):
            image_path = os.path.join(folder_path, filename)
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    logger.info(f"✅ 找到圖片: {filename} → 位置: {location}")
                    return location  # ✅ 找到就跳出，結束函式
            except Exception as e:
                logger.warning(f"⚠️ 無法辨識 {filename}: {e}")
            time.sleep(0.2)  # 避免CPU過高

    logger.info("❌ 沒有找到任何符合的圖片")
    return None

def is_yellow_on_side(image_path, threshold=150, sample_step=1):
    """
    使用 OpenCV 判斷圖片中黃色點是否靠右邊。
    回傳:
      True  → 黃點靠右
      False → 黃點靠左或沒找到
    """
    # 讀取圖片 (BGR)
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 無法讀取圖片: {image_path}")
        return False

    # 轉換為 RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img_rgb.shape

    # 每隔 sample_step 取樣一次以提高效率
    pixels = img_rgb[::sample_step, ::sample_step]

    # 分離通道
    r = pixels[:, :, 0]
    g = pixels[:, :, 1]
    b = pixels[:, :, 2]

    # 建立黃色遮罩（紅、綠高、藍低）
    mask = (r > threshold) & (g > threshold) & (b < threshold / 2)
    y_indices, x_indices = np.where(mask)

    if len(x_indices) == 0:
        return False  # 沒偵測到黃色點

    # 找最左與最右的 x 座標
    min_x = np.min(x_indices)
    max_x = np.max(x_indices)

    # 計算距離左右邊界
    dist_left = min_x
    dist_right = w - max_x
    left_ratio = dist_left / w
    right_ratio = dist_right / w
    logger.info(f"🟡 黃點位置比例 - 左: {left_ratio:.2f}, 右: {right_ratio:.2f}")
    
    if left_ratio < 0.10:
        return False
    elif  right_ratio < 0.10:
        return True
    else:
        # 若右邊距離更短，代表靠右
        return dist_right < dist_left