import pyautogui

# ====== 在畫面上尋找工具列位置 ======
# 增加傳入參數，代表辨識兩次的圖片
def GetImgLocation(image1, image2):
    '''
    在畫面上尋找工具列位置
    '''
    try:
        tool1_location = pyautogui.locateOnScreen(image1, confidence=0.7)
    except pyautogui.ImageNotFoundException:
        try:
            tool1_location = pyautogui.locateOnScreen(image2, confidence=0.7)
        except pyautogui.ImageNotFoundException:
            tool1_location = None
    return tool1_location