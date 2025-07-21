import pyautogui
import sys
from datetime import datetime

# Save screenshot with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"screenshot_{timestamp}.png"
path = f"./screenshots/{filename}"

# Create folder if not exists
import os
os.makedirs("screenshots", exist_ok=True)

image = pyautogui.screenshot()
image.save(path)

# Print path so Electron can read it
print(path)
