import base64
from PIL import Image, ImageDraw, ImageFont
import io
import configparser
import requests
import threading
import queue
import time

# Constants
VERSION = "2.3"
WIDTH, HEIGHT = 6000, 5800

# Load configuration from ini file
config = configparser.ConfigParser()
config.read("settings/nm_config.ini")

# Bitmaps dictionary with placeholders (add other bitmaps as needed)
bitmaps = {
    "pBMbabylove": None,  # Placeholder: Replace with Image.open(io.BytesIO(base64.b64decode("...")))
    "pBMballoonaura": None,  # Placeholder: Replace with Image.open(io.BytesIO(base64.b64decode("...")))
    "pBMbear": None,  # Placeholder: Replace with Image.open(io.BytesIO(base64.b64decode("...")))
    "pBMbombcombo": None,  # Placeholder: Replace with Image.open(io.BytesIO(base64.b64decode("...")))
    "pBMboost": None,  # Placeholder: Replace with Image.open(io.BytesIO(base64.b64decode("...")))
    # Add more bitmaps here as needed, e.g., "pBMTimer", "pBMNatroLogo", etc.
}

# Initialize the main image (similar to pBMReport in AHK)
def create_report_image():
    # Create a new image with Pillow
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))  # Black background
    draw = ImageDraw.Draw(image)
    
    # Example: Draw a simple title (you'll expand this with the full logic later)
    try:
        font = ImageFont.truetype("segoeui.ttf", 64)  # Adjust font path as needed
    except:
        font = ImageFont.load_default()  # Fallback to default font
    draw.text((WIDTH // 2, 50), "Hourly Report", font=font, fill="white", anchor="mm")
    
    # Placeholder for further sections (status, buffs, timers, stats, info)
    # Add your logic here to draw bitmaps and text as per the AHK script
    
    return image

# Function to send the image to Discord (via webhook or bot)
def send_to_discord(image):
    webhook = config.get("Status", "webhook", fallback="")
    bottoken = config.get("Status", "bottoken", fallback="")
    discord_mode = config.getint("Status", "discordMode", fallback=0)
    channel_id = config.get("Status", "ReportChannelID", fallback=config.get("Status", "MainChannelID", fallback=""))

    if not webhook and not bottoken:
        print("No Discord webhook or bot token configured.")
        return

    # Save image to a byte stream
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Prepare Discord payload
    if discord_mode == 0:  # Webhook mode
        url = webhook
        files = {"file.png": ("file.png", img_byte_arr, "image/png")}
        payload = {
            "embeds": [{
                "title": f"**[{time.strftime('%H:%M:00')}] Hourly Report**",
                "color": 14052794,
                "image": {"url": "attachment://file.png"}
            }]
        }
        response = requests.post(url, data={"payload_json": str(payload)}, files=files)
    else:  # Bot mode
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {bottoken}",
            "User-Agent": "DiscordBot (Python, requests)"
        }
        files = {"file": ("file.png", img_byte_arr, "image/png")}
        payload = {
            "embeds": [{
                "title": f"**[{time.strftime('%H:%M:00')}] Hourly Report**",
                "color": 14052794,
                "image": {"url": "attachment://file.png"}
            }]
        }
        response = requests.post(url, headers=headers, data={"payload_json": str(payload)}, files=files)

    if response.status_code != 200:
        print(f"Failed to send report to Discord: {response.text}")
    else:
        print("Report sent successfully!")

# Main execution
if __name__ == "__main__":
    report_image = create_report_image()
    send_to_discord(report_image)