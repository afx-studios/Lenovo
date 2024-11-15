import time
from pynput import mouse, keyboard

def on_press(key):
    try:
        # If the key has a char attribute, it's an alphanumeric key
        print(f"Alphanumeric key {key.char} pressed")
    except AttributeError:
        # If not, it's a special key (like F1, space, etc.)
        print(f"Special key {key} pressed")

def on_release(key):
    try:
        # Handling key release
        print(f"Alphanumeric key {key.char} released")
    except AttributeError:
        print(f"Special key {key} released")

    # Stop listener if 'esc' is pressed
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse button '{button}' pressed at ({x}, {y})")
    else:
        print(f"Mouse button '{button}' released at ({x}, {y})")

def on_scroll(x, y, dx, dy):
    print(f"Mouse scrolled at ({x}, {y}) - dx: {dx}, dy: {dy}")

if __name__ == "__main__":
    # Start the keyboard listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    # Start the mouse listener
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    print("Listening for HID inputs. Press ESC to exit.")

    try:
        # Keep the script running to listen for events
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle the case where Ctrl+C is pressed
        print("Script was interrupted by user.")

    finally:
        # Ensure listeners are stopped properly
        keyboard_listener.stop()
        mouse_listener.stop()
        print("Listeners stopped")
