#MapleStory Worlds-ChronoStory
import pygetwindow as gw
import pyautogui
import time
import keyboard
import threading
from ocr_reader import get_mp_from_image  # ✅ 匯入 EasyOCR 模組
from src.utils.logger import logger
from src.utils.common import (GetImgLocation,find_images_in_folder,is_yellow_on_side)
from src.utils.discordtool import send_discord_notification

# ====== 全域變數 ======
running = False  # 控制程式是否執行
check_hp = True  # 控制是否檢查HP
check_mp = True  # 控制是否檢查MP
press_v = False  # 控制是否自動按V鍵
press_c = False  # 控制是否自動按C鍵
press_move = False  # 控制是否自動左右移動
v_thread = None  # 儲存按V的執行緒
c_thread = None  # 儲存按C的執行緒
move_thread = None  # 儲存移動執行緒
move_direction = 'right'  # 當前移動方向：'right' 或 'left'
move_duration = 30  # 當找不到邊界圖示時，每次持續移動秒數

# ====== 取得 ChronoStory 視窗位置 ======
try:
    win_list  = gw.getWindowsWithTitle('MapleStory Worlds-ChronoStory')
    if not win_list :
        logger.error("❌ 找不到 ChronoStory 視窗，請確認程式已啟動並登入遊戲！")
        exit(1)
    win=win_list[0]
    logger.info(f"取得 ChronoStory 視窗位置:{win}")   
    send_discord_notification(f"取得 ChronoStory 視窗位置:{win}","MapleStory Worlds-ChronoStory 自動補血補魔程式",0xFF5733)
    win.resizeTo(1322,744)
    x, y = win.left, win.top
    logger.info(f"視窗位置 x:{x} y:{y} width:{win.width} height:{win.height}")
    send_discord_notification(f"視窗位置 x:{x} y:{y} width:{win.width} height:{win.height}","MapleStory Worlds-ChronoStory 自動補血補魔程式",0xFF5733)
except Exception as e:
    logger.error(f"❌ 取得或調整 ChronoStory 視窗大小時發生錯誤: {e}")
    exit(1)



# ====== 在畫面上尋找 MP 標示區域 ======
def get_mp_ratio():
    """擷取 MP 區域並回傳比值 (0~1)"""
    try:
        MPlocation = pyautogui.locateOnScreen('MP.png', confidence=0.6)
    except pyautogui.ImageNotFoundException:
        try:
            MPlocation = pyautogui.locateOnScreen('MP2.png', confidence=0.6)
        except pyautogui.ImageNotFoundException:
            MPlocation = None
    
    if MPlocation:
        MPregion = (int(MPlocation.left), int(MPlocation.top), int(MPlocation.width), int(MPlocation.height))        

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
    try:
        HPlocation = pyautogui.locateOnScreen('HP.png', confidence=0.5)
    except pyautogui.ImageNotFoundException:
        try:
            HPlocation = pyautogui.locateOnScreen('HP2.png', confidence=0.5)
        except pyautogui.ImageNotFoundException:
            HPlocation = None
    
    if HPlocation:
        HPregion = (int(HPlocation.left), int(HPlocation.top), int(HPlocation.width), int(HPlocation.height))
        #print('region:', region)

        # 確保 region 是四個整數
        if all(isinstance(i, int) for i in HPregion):
            mp_img = pyautogui.screenshot(region=HPregion)
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

    
    try:
        tool1_location = pyautogui.locateOnScreen('tool1.png', confidence=0.7)
    except pyautogui.ImageNotFoundException:
        try:
            tool1_location = pyautogui.locateOnScreen('tool2.png', confidence=0.7)
        except pyautogui.ImageNotFoundException:
            tool1_location = None
    
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
    #on_f9_press()
    print("程式已啟動！按 F6 可暫停")

def on_f6_press(e):
    global running
    running = False    
    #on_f9_press()
    print("程式已暫停！按 F5 可重新啟動")

# ====== V 鍵自動按壓函數 ======
def auto_press_v():
    """獨立執行緒：自動每秒按一次 V 鍵"""
    while press_v:
        keyboard.press_and_release('v')
        #print("🔄 自動按下 V 鍵（獨立執行緒）")
        time.sleep(0.5)  # 每秒按一次 V 鍵

def auto_press_c():
    """獨立執行緒：自動每秒按一次 C 鍵"""
    while press_c:
        keyboard.press_and_release('c')
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
        
def on_f8_press(e):
    global press_c, c_thread
    press_c = not press_c
    
    if press_c:
        # 如果開啟了 V 鍵功能，啟動新執行緒
        print("🟢 自動按C功能：開啟")
        c_thread = threading.Thread(target=auto_press_c)
        c_thread.daemon = True  # 設為守護線程，主程式結束時自動終止
        c_thread.start()
    else:
        print("🔴 自動按C功能：關閉")

def on_ctrl_q_press():
    """Ctrl+Q 退出程式"""
    global running, press_v
    print("🛑 收到 Ctrl+Q，正在退出程式...")
    running = False
    press_v = False  # 停止自動按V功能
    global press_move
    press_move = False  # 停止自動移動功能
    import os    
    
    # 強制終止所有執行緒並退出程式
    os._exit(0)

# ====== 自動左右移動功能 ======
def find_edge(edge_left='left_edge.png', edge_right='right_edge.png'):
    """嘗試找到畫面左/右邊界的圖片位置；找不到回傳 (None, None)"""
    left_loc = None
    right_loc = None
    try:
        left_loc = pyautogui.locateOnScreen(edge_left, confidence=0.7)
        print('left_loc:', left_loc)
    except Exception:
        left_loc = None
    try:
        right_loc = pyautogui.locateOnScreen(edge_right, confidence=0.7)
        print('right_loc:', right_loc)
    except Exception:
        right_loc = None
    return left_loc, right_loc

def auto_move():
    """在獨立執行緒中自動左右移動，偵測到邊界則反向，找不到邊界則以時間為基準反向"""
    global press_move, move_direction, move_duration
    last_switch = time.time()
    try:
        while press_move:
            last_switch = time.time()
            # 嘗試以圖像偵測邊界
            #left_loc, right_loc = find_edge()
            # if is_yellow_on_side("minMap.png"):
            #     logger.info('偵測到右邊界，改為向左移動')
            #     keyboard.press('alt+left+v+z')
            #     time.sleep(10)
            #     keyboard.release('alt+left+v+z')
            # else:
            #     logger.info('偵測到左邊界，改為向右移動')
            #     keyboard.press('alt+right+v+z')
            #     time.sleep(10)
            #     keyboard.release('alt+right+v+z')



            # if is_yellow_on_side("minMap.png"):
            #     if move_direction=='right':
            #         move_direction='left'
            #     else:
            #         move_direction='right'

            if move_direction == 'right':
            #     # 若偵測到右邊界，則轉向
            #     if not is_yellow_on_side("minMap.png"):
            #         print('偵測到右邊界，改為向左移動')
            #         keyboard.press('alt+right+v+z')
            #         time.sleep(5)
            #         keyboard.release('alt+right+v+z')
                move_direction = 'left'
            #         last_switch = time.time()
            #         continue
            #     # 向右按下並保持短暫
                keyboard.press('right+v+z')
                time.sleep(10)
                keyboard.release('right+v+z')
            else:
            #     # move_direction == 'left'
            #     if  is_yellow_on_side("minMap.png"):
            #         print('偵測到左邊界，改為向右移動')
            #         keyboard.press('alt+left+v+z')
            #         time.sleep(5)
            #         keyboard.release('alt+left+v+z')
                move_direction = 'right'
            #         last_switch = time.time()
            #         continue
                keyboard.press('left+v+z')
                time.sleep(10)
                keyboard.release('left+v+z')

            # 如果超過 move_duration 秒沒有偵測到邊界，則反向（time-based fallback）
            # if time.time() - last_switch >= move_duration:
            #     move_direction = 'left' if move_direction == 'right' else 'right'
            #     print(f'超過 {move_duration}s，時間回退反向為 {move_direction}')
            #     last_switch = time.time()

            # 小停頓，避免佔滿 CPU
            time.sleep(1)
    finally:
        # 確保在結束時釋放任何可能被按住的鍵
        try:
            keyboard.release('left')
            keyboard.release('right')
        except Exception:
            pass

def on_f9_press():
    """切換自動左右移動功能（F9）"""
    global press_move, move_thread, move_direction
    press_move = not press_move
    if press_move:
        logger.info('🟢 自動左右移動：開啟')
        # 啟動移動執行緒
        move_thread = threading.Thread(target=auto_move)
        move_thread.daemon = True
        move_thread.start()
    else:
        logger.info('🔴 自動左右移動：關閉')
        # move_thread 會在下一次迴圈檢查 press_move 後結束

# 註冊熱鍵
keyboard.on_press_key("f3", on_f3_press)
keyboard.on_press_key("f4", on_f4_press)
keyboard.on_press_key("f5", on_f5_press)
keyboard.on_press_key("f6", on_f6_press)
keyboard.on_press_key("f7", on_f7_press)
keyboard.on_press_key("f8", on_f8_press)
keyboard.add_hotkey("ctrl+f9", on_f9_press)
keyboard.add_hotkey("ctrl+q", on_ctrl_q_press)


# ====== 小地圖紅點偵測與暫停/還原功能 ======
paused_by_red = False

def check_minimap_for_red(sample_step=8, red_threshold=200):
    """在視窗右上角的區域採樣，偵測是否有明顯的紅色像素存在。
    - sample_step: 每隔多少像素採樣以加速偵測
    - red_threshold: R 值的閾值（同時要求 G,B 明顯低於 R）
    回傳 True 表示偵測到紅點，否則 False。
    """
    try:
        #抓小地圖位置
        SMaplocation= find_images_in_folder()
        
        if SMaplocation:
            logger.info(f"小地圖位置:{SMaplocation}")
            SMapregion = (int(SMaplocation.left), int(SMaplocation.top), int(SMaplocation.width), int(SMaplocation.height))
            if all(isinstance(i, int) for i in SMapregion):
                img = pyautogui.screenshot(region=SMapregion)
                img.save("minMap.png")  # 可選：儲存擷取畫面
                
                px = img.load()
                w, h = img.size
                for ix in range(0, w, sample_step):
                    for iy in range(0, h, sample_step):
                        r, g, b = px[ix, iy][:3]
                        if r >= red_threshold and g < (red_threshold // 2) and b < (red_threshold // 2):
                            return True
                return False
            else:
                logger.info("小地圖抓取失敗")
                return None
    except Exception:
        return False

def gotoTrade():
    """移動到交易區域"""
    # 這邊可以加入移動到交易區域的程式碼
    Tradelocation= GetImgLocation('trade.png','trade1.png')
    if Tradelocation:
        Traderegion = (int(Tradelocation.left), int(Tradelocation.top), int(Tradelocation.width), int(Tradelocation.height))
        if all(isinstance(i, int) for i in Traderegion):
            # 取得中心點座標
            x = Tradelocation.left + Tradelocation.width / 2
            y = Tradelocation.top + Tradelocation.height / 2

            # 在中心點點擊滑鼠左鍵
            pyautogui.click(x, y, button='left')   
            pass


# ====== 主迴圈 ======
print("程式已準備就緒！")
print("按 F5 開始執行")
print("按 F6 暫停程式")
print("按 F3 切換HP檢測")
print("按 F4 切換MP檢測")
print("按 F7 切換自動按V功能")
print("按 F8 切換自動按C功能")
print("按 Ctrl+F9 切換左右移動+V功能")
print("按 Ctrl+Q 退出程式")

while True:
    try:
        # 每次迴圈先檢查小地圖是否有紅點，若有則暫停所有自動功能
        # try:
        #     red_found = check_minimap_for_red()
        # except Exception:
        #     red_found = False
        if running:
            # if red_found and not paused_by_red:
            #     paused_by_red = True
            #     print("偵測到小地圖紅點，透過 F6 暫停程式，並跳出主迴圈")
            #     send_discord_notification("偵測到小地圖紅點，程式已自動暫停！","MapleStory Worlds-ChronoStory 自動補血補魔程式",0xFF0000)
            #     on_f6_press(None)  # 直接呼叫 F6 的處理函式來暫停
            #     time.sleep(1)
            #     # 這邊可以控制抓取圖片同的位置點選滑鼠左鍵
            #     #gotoTrade()
            #     break
           

            if check_mp:
                mp_ratio = get_mp_ratio()    
                if mp_ratio is not None:
                    if mp_ratio < 0.2:
                        # 自動喝水
                        keyboard.press_and_release('insert')
                        logger.info("🧃 MP 低於 20%，自動按下 Insert！")
                    else:
                        logger.info(f"MP 正常 ({mp_ratio*100:.1f}%)")
                else:
                    logger.info("⚠️ 無法取得 MP 值")

            if check_hp:
                hp_ratio = get_hp_ratio()    
                if hp_ratio is not None:
                    if hp_ratio < 0.8:
                        # 自動喝水
                        keyboard.press_and_release('delete')
                        logger.info("🧃 HP 低於 80%，自動按下 Delete")
                    else:
                        logger.info(f"HP 正常 ({hp_ratio*100:.1f}%)")
                else:
                    logger.info("⚠️ 無法取得 HP 值")
            
            # 定期按下 Z 鍵保持角色活躍：改為每 10 秒按一次
            #keyboard.press_and_release('z')
            #print("🔄 自動按下 V 鍵（獨立執行緒）")
            time.sleep(0.5)  # 每秒按一次 V 鍵
            # 判斷 get_tool1_position() 是NULL 的時候按下`按鍵
            # tool_location=get_tool1_position()  # 偵測 tool1 位置
            # if tool_location is None:
            #     keyboard.press_and_release('`')
            #     time.sleep(1)  # 等待一秒讓畫面更新
            #     print("按下 ` 鍵以嘗試重新顯示工具列")
            # else:
            #     print("tool1 位置：", tool_location)
                        
        # 減少CPU使用率
        time.sleep(3)
    except KeyboardInterrupt:
        print("🛑 程式被中斷，正在退出...")
        break
    
