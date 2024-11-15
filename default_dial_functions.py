import keyboard

def on_press(key):
    print(f"Key pressed: {key}")

keyboard.on_press(on_press)

print("Press any key on the Lenovo Dial...")
keyboard.wait()
