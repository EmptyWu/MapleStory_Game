#MapleStory Worlds-ChronoStory
import pygetwindow as gw
import pyautogui
import time
import keyboard
import threading
from ocr_reader import get_mp_from_image  # ✅ 匯入 EasyOCR 模組
from src.utils.logger import logger
from src.utils.common import (GetImgLocation)

# ====== 全域變數 ======
running = False  # 控制程式是否執行
check_hp = True  # 控制是否檢查HP
check_mp = True  # 控制是否檢查MP
press_v = False  # 控制是否自動按V鍵
v_thread = None  # 儲存按V的執行緒

# ====== 取得 ChronoStory 視窗位置 ======
win = gw.getWindowsWithTitle('MapleStory Worlds-ChronoStory')[0]
logger.info(f"取得 ChronoStory 視窗位置:{win}")   
#print("win:", win)
x, y = win.left, win.top
logger.info(f"視窗位置 x:{x} y:{y} width:{win.width} height:{win.height}")
#print("x:", x,"y",y,'width',win.width,'height',win.height)

# ====== 在畫面上尋找 MP 標示區域 ======
def get_mp_ratio():
    """擷取 MP 區域並回傳比值 (0~1)"""
    
    MPlocation = GetImgLocation('MP2.png', 'MP.png')
    
    if MPlocation:
        MPregion = (int(MPlocation.left), int(MPlocation.top), int(MPlocation.width), int(MPlocation.height))
        #print('region:', MPregion)

        # 確保 region 是四個整數
        if all(isinstance(i, int) for i in MPregion):
            mp_img = pyautogui.screenshot(region=MPregion)
            mp_img.save("mp_capture.png")  # 可選：儲存擷取畫面
            
            #print("✅ 成功擷取 MP 區域，開始 OCR 解析...")

            # 使用 EasyOCR 模組辨識
            ratio = get_mp_from_image("mp_capture.png","MP")
            return ratio
        else:
            #print("region 格式錯誤")
            return None
    else:
        print("找不到 MP 圖示或不在視窗範圍內")
        return None
    
# ====== 在畫面上尋找 HP 標示區域 ======
def get_hp_ratio():
    """擷取 HP 區域並回傳比值 (0~1)"""
    HPlocation = GetImgLocation('HP2.png', 'HP.png')
    
    if HPlocation:
        region = (int(HPlocation.left), int(HPlocation.top), int(HPlocation.width), int(HPlocation.height))
        #print('region:', region)

        # 確保 region 是四個整數
        if all(isinstance(i, int) for i in region):
            mp_img = pyautogui.screenshot(region=region)
            mp_img.save("hp_capture.png")  # 可選：儲存擷取畫面
            
            #print("✅ 成功擷取 HP 區域，開始 OCR 解析...")

            # 使用 EasyOCR 模組辨識
            ratio = get_mp_from_image("hp_capture.png","HP")
            return ratio
        else:
            #print("region 格式錯誤")
            return None
    else:
        print("找不到 HP 圖示或不在視窗範圍內")
        return None

# ====== 在畫面上尋找 tool1.png 標示區域 ======
def get_tool1_position():
    """尋找 tool1.png 並回傳中心位置"""

    tool1_location = GetImgLocation('tool1.png', 'tool2.png')
    
    if tool1_location:
        center_x = tool1_location.left + tool1_location.width // 2
        center_y = tool1_location.top + tool1_location.height // 2
        return (center_x, center_y)
    else:
        print("找不到 tool1 圖示或不在視窗範圍內")
        return None

# ====== 按鍵控制功能 ======
def on_f3_press(e):
    global check_hp
    check_hp = not check_hp
    print(f"HP檢測狀態：{'開啟' if check_hp else '關閉'}")

def on_f4_press(e):
    global check_mp
    check_mp = not check_mp
    print(f"MP檢測狀態：{'開啟' if check_mp else '關閉'}")

def on_f5_press(e):
    global running
    running = True
    print("程式已啟動！按 F6 可暫停")

def on_f6_press(e):
    global running
    running = False
    print("程式已暫停！按 F5 可重新啟動")

# ====== V 鍵自動按壓函數 ======
def auto_press_v():
    """獨立執行緒：自動每秒按一次 V 鍵"""
    while press_v:
        keyboard.press_and_release('v')
        #print("🔄 自動按下 V 鍵（獨立執行緒）")
        time.sleep(0.5)  # 每秒按一次 V 鍵

def on_f7_press(e):
    global press_v, v_thread
    press_v = not press_v
    
    if press_v:
        # 如果開啟了 V 鍵功能，啟動新執行緒
        print("🟢 自動按V功能：開啟")
        v_thread = threading.Thread(target=auto_press_v)
        v_thread.daemon = True  # 設為守護線程，主程式結束時自動終止
        v_thread.start()
    else:
        # 如果關閉了 V 鍵功能，等待執行緒結束
        print("🔴 自動按V功能：關閉")
        # press_v 已經設為 False，執行緒會自行結束

def on_ctrl_q_press():
    """Ctrl+Q 退出程式"""
    global running, press_v
    print("🛑 收到 Ctrl+Q，正在退出程式...")
    running = False
    press_v = False  # 停止自動按V功能
    import os    
    
    # 強制終止所有執行緒並退出程式
    os._exit(0)

# 註冊熱鍵
keyboard.on_press_key("f3", on_f3_press)
keyboard.on_press_key("f4", on_f4_press)
keyboard.on_press_key("f5", on_f5_press)
keyboard.on_press_key("f6", on_f6_press)
keyboard.on_press_key("f7", on_f7_press)
keyboard.add_hotkey("ctrl+q", on_ctrl_q_press)

# ====== 主迴圈 ======
print("程式已準備就緒！")
print("按 F5 開始執行")
print("按 F6 暫停程式")
print("按 F3 切換HP檢測")
print("按 F4 切換MP檢測")
print("按 F7 切換自動按V功能")
print("按 Ctrl+Q 退出程式")

while True:
    try:
        if running:
            if check_mp:
                mp_ratio = get_mp_ratio()    
                if mp_ratio is not None:
                    if mp_ratio < 0.2:
                        # 自動喝水
                        keyboard.press_and_release('insert')
                        print("🧃 MP 低於 20%，自動按下 Insert！")
                    else:
                        print(f"MP 正常 ({mp_ratio*100:.1f}%)")
                else:
                    print("⚠️ 無法取得 MP 值")

            if check_hp:
                hp_ratio = get_hp_ratio()    
                if hp_ratio is not None:
                    if hp_ratio < 0.8:
                        # 自動喝水
                        keyboard.press_and_release('delete')
                        print("🧃 HP 低於 80%，自動按下 Delete")
                    else:
                        print(f"HP 正常 ({hp_ratio*100:.1f}%)")
                else:
                    print("⚠️ 無法取得 HP 值")
            # 判斷 get_tool1_position() 是NULL 的時候按下`按鍵
            tool_location=get_tool1_position()  # 偵測 tool1 位置
            if tool_location is None:
                keyboard.press_and_release('`')
                time.sleep(1)  # 等待一秒讓畫面更新
                print("按下 ` 鍵以嘗試重新顯示工具列")
            else:
                print("tool1 位置：", tool_location)
                        
        # 減少CPU使用率
        time.sleep(3)
    except KeyboardInterrupt:
        print("🛑 程式被中斷，正在退出...")
        break
    
