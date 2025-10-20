import pyautogui
#import win32gui

# ====== 在畫面上尋找工具列位置 ======
# 增加傳入參數，代表辨識兩次的圖片
def GetImgLocation(image1, image2):
    '''
    在畫面上尋找工具列位置
    '''
    tool1_location = None
    print("image1", image1)
    try:
        tool1_location = pyautogui.locateOnScreen(image1, confidence=0.7)
    except pyautogui.ImageNotFoundException:
        try:
            tool1_location = pyautogui.locateOnScreen(image2, confidence=0.7)
        except pyautogui.ImageNotFoundException:
            tool1_location = None
    return tool1_location

# def resize_window(window_title, width=1642, height=923):
#     # 取得視窗句柄
#     hwnd = win32gui.FindWindow(None, window_title)
#     if hwnd == 0:
#         print(f"找不到視窗: {window_title}")
#         return

#     # 取得目前視窗位置
#     rect = win32gui.GetWindowRect(hwnd)
#     x, y = rect[0], rect[1]  # 保持視窗左上角位置不變

#     # 調整視窗大小
#     win32gui.MoveWindow(hwnd, x, y, width, height, True)
#     print(f"已將「{window_title}」調整為 {width}x{height}")