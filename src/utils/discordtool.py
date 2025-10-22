# discordtool.py
# ========================
# ChronoStory Discord 通知工具
# 用法:
#   from discordtool import send_discord_notification
#   send_discord_notification("你的訊息內容")

import requests
from src.utils.logger import logger
import json

# ---- 請設定你的 Discord Webhook URL ----
WEBHOOK_URL = "https://discord.com/api/webhooks/1430095916202725478/MyeBxjb4fmwv32_Zq1x0uU1rcXclTBrtD_DDWBR_pnNZneCg60DJrkfdOwFjyGMwRBiB"


def send_discord_notification(message: str, username: str = "ChronoStory Bot", color: int = 0x00FFAA):
    """
    發送一則 Discord 通知到指定頻道。
    支援基本文字與嵌入訊息格式。

    參數:
        message (str): 要發送的文字內容
        username (str): 顯示在 Discord 上的名稱 (預設: ChronoStory Bot)
        color (int): Embed 顏色 (預設: 綠色)
    """

    if not WEBHOOK_URL or "discord.com/api/webhooks/" not in WEBHOOK_URL:
        logger.error("❌ [DiscordTool] Webhook URL 尚未設定！")
        return False

    embed = {
        "description": message,
        "color": color
    }

    data = {
        "username": username,
        "embeds": [embed]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code in (200, 204):
            logger.info(f"✅ [DiscordTool] 已通知: {message}")
            return True
        else:
            logger.info(f"⚠️ [DiscordTool] 發送失敗 ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ [DiscordTool] 發送錯誤: {e}")
        return False


# ---- 非同步版本 (可選) ----
# 適合 asyncio 架構使用
async def async_send_discord_notification(message: str, username: str = "ChronoStory Bot", color: int = 0x00FFAA):
    import aiohttp
    async with aiohttp.ClientSession() as session:
        embed = {
            "description": message,
            "color": color
        }
        data = {
            "username": username,
            "embeds": [embed]
        }
        try:
            async with session.post(WEBHOOK_URL, json=data) as resp:
                if resp.status in (200, 204):
                    logger.info(f"✅ [DiscordTool] 已通知: {message}")
                else:
                    logger.info(f"⚠️ [DiscordTool] 發送失敗: {resp.status}")
        except Exception as e:
            logger.error(f"❌ [DiscordTool] 發送錯誤: {e}")
