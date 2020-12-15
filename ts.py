try:
    import PIL.ImageGrab as ss
    from PIL import Image
except ImportError:
    print("Pillow is required")
try:
    import pytesseract
except ImportError:
    print("pytesseract and tesseract-ocr is required")
try:
    import keyboard
except ImportError:
    print("keyboard module is required")
try:
    import pyperclip
except ImportError:
    print("pyperclip is required")
try:
    from pynput.mouse import Controller
except ImportError:
    print("pynput is required")
import ctypes
import re
import os
import sys
import time
import getopt


def usage():
    print("""TextScanner - scanning text from images
    Usage: ts.py [OPTIONS]
    Options:
    -h --help - display help
    -f --file [FILE NAME] - save results to txt file
    -k --key - scan for keys
    -c --clipboard - copy to clipboard

    \\ - use to set area. if not set will be used last value
    \' - use to quit program
    ]  - use to scan text
    """)

def ssTake():
    return ss.grab()

def deleteFile(filename):
    os.remove(filename)

def cropImg(screenshot, x, y, width, height):
    cropped = screenshot.crop((x, y, x+width, y+height))
    return cropped

def findKey(img):
    try:
        rawKey = pytesseract.image_to_string(img)
        key = re.search("[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}", rawKey).group()
        return key
    except AttributeError:
        return "Nothing found"

def getKeyFromImage(x, y, width, height):
    screenshot = ssTake()
    cropped = cropImg(screenshot, x, y, width, height)
    return findKey(cropped)

def scanTextFromImage(x, y, width, height):
    screenshot = ssTake()
    cropped = cropImg(screenshot, x, y, width, height)
    return pytesseract.image_to_string(cropped)

def saveToFile(scanned, file):
    with open(file, 'w') as f:
        f.write(scanned)
    return f"Results saved to file: {file}"

def defaultFileSettings(settings_file):
    with open(settings_file, "w") as f:
            f.write("10 10\n10 10")

def readAndCheckDataFromFile(settings_file):
    while True:
        with open(settings_file, "r") as f:
            sets = f.readlines()

        if len(sets) != 2:
            defaultFileSettings(settings_file)
            continue

        if len(sets[0].split(' ')) != 2 or len(sets[1].split(' ')) != 2:
            defaultFileSettings(settings_file)
            continue

        x, y = sets[0].strip().split(' ')
        height, width = sets[1].strip().split(' ')
        if not ("".join((x, y, height, width))).isdigit():
            defaultFileSettings(settings_file)
            continue
        
        return (int(x), int(y), int(height), int(width))

if __name__ == "__main__":
    to_file, key, to_clipboard = False, False, False
    f1 = True
    file_name = ""
    settings_file = "settings"
    if (not os.path.exists(settings_file)) or os.stat(settings_file).st_size == 0:
        defaultFileSettings(settings_file)

    x, y, height, width = readAndCheckDataFromFile(settings_file)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hckf:", ["help", "clipboard", "file", "key"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        exit()
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            exit()
        elif o in ("-f", "--file"):
            to_file = True
            file_name = a
        elif o in ("-c", "--clipboard"):
            to_clipboard = True
        elif o in ("-k", "--key"):
            key = True
        else:
            print("Wrong options. Manual:")
            usage()
            exit()
    print("Running\n")
    while True:
        if keyboard.is_pressed(']'):
            if key:
                scanned = getKeyFromImage(x, y, width, height)
            else:
                scanned = scanTextFromImage(x, y, width, height)

            print(scanned)
            if to_file:
                print(saveToFile(scanned, file_name))
            if to_clipboard:
                pyperclip.copy(scanned)

            time.sleep(0.3)
        elif keyboard.is_pressed('`'):
            break
        elif keyboard.is_pressed('\\'):
            mouse = Controller()
            if f1:
                f1 = False
                x,y = mouse.position
                print("X Y coordinates set")
            else:
                f1 = True
                x1,y1 = mouse.position
                if x > x1:
                    width = x-x1
                    x=x1
                else:
                    width = x1-x
                if y > y1:
                    height = y-y1
                    y=y1
                else:
                    height = y1-y
                with open("settings", "w") as f:
                    f.write(f"{x} {y}\n{height} {width}")
                print(f"X Y = {x}, {y} | height width = {height}, {width}\n\n")
            time.sleep(0.2)
        time.sleep(0.08)
