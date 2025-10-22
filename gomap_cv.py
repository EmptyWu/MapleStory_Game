# from PIL import Image

# def has_yellow_dot(image_path, threshold=150, sample_step=1):
#     img = Image.open(image_path).convert("RGB")
#     px = img.load()
#     w, h = img.size

#     for x in range(0, w, sample_step):
#         for y in range(0, h, sample_step):
#             r, g, b = px[x, y]
#             # 黃色：紅、綠都高，藍低
#             if r > threshold and g > threshold and b < threshold / 2:
#                 return True
#     return False


# # 測試
# image_path = r"F:\OneDrive - 7058mn\Desktop\MapleStory_Game\minmaps\ColdField1.png"  # 你的圖
# if has_yellow_dot(image_path):
#     print("✅ 圖片中有黃色點！")
# else:
#     print("❌ 圖片中沒有黃色點。")

import cv2
import numpy as np

def is_yellow_on_right(image_path, threshold=150, sample_step=1):
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
    print(f"🟡 黃點位置比例 - 左: {left_ratio:.2f}, 右: {right_ratio:.2f}")

    # 若右邊距離更短，代表靠右
    return left_ratio <0.1 or right_ratio <0.1

if is_yellow_on_right("minMap.png"):
    print("✅ 黃點靠近邊")
else:
    print("❌ 黃點不在右邊或沒找到黃色點")