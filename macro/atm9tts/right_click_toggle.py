import threading
import time
import os
from ctypes import windll, Structure, c_long, byref

class Point(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_cursor_position():
    point = Point()
    windll.user32.GetCursorPos(byref(point))
    return point.x, point.y

# Constants for mouse events
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Constants for keyboard states
VK_Y = 0x59
VK_T = 0x54

# Flag to track if clicking should be active
clicking = False

# Function to simulate mouse clicks
def clicker_thread():
    global clicking
    while True:
        if clicking:
            x, y = get_cursor_position()
            windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
            windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
            time.sleep(0.001)  # Short delay to prevent system overload
        else:
            time.sleep(0.01)

# Function to monitor keyboard input
def keyboard_monitor():
    global clicking
    while True:
        if windll.user32.GetAsyncKeyState(VK_Y) & 0x8000:
            clicking = not clicking
            print(f"Clicking {'enabled' if clicking else 'disabled'}")
            time.sleep(0.2) # Debounce delay.

        if windll.user32.GetAsyncKeyState(VK_T) & 0x8000:
            print("Exiting program...")
            os._exit(0)

        time.sleep(0.01)  # Small delay for keyboard checking

print("Auto Right Clicker started")
print("Press Y to toggle auto right-click")
print("Press T to exit")

click_thread = threading.Thread(target=clicker_thread, daemon=True)
click_thread.start()

keyboard_thread = threading.Thread(target=keyboard_monitor, daemon=True)
keyboard_thread.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program interrupted by user")