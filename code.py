
import time
import board
import digitalio
import usb_hid

STARTUP_DELAY   = 5.0
CHAR_DELAY      = 0.045
LINE_DELAY      = 0.450
KEY_HOLD        = 0.025

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def blink(n, on=0.15, off=0.15):
    for _ in range(n):
        led.value = True;  time.sleep(on)
        led.value = False; time.sleep(off)

kbd = None
for d in usb_hid.devices:
    if d.usage_page == 0x01 and d.usage == 0x06:
        kbd = d
        break
if kbd is None:
    raise RuntimeError("No HID keyboard device found — is boot.py installed?")

_EMPTY = bytearray(8)
_report = bytearray(8)

MOD_LSHIFT = 0x02

def _press(mod, keycode):

    if mod:
        _report[0] = mod
        kbd.send_report(_report)
        time.sleep(0.005)

    # 2. Press the primary key
    _report[2] = keycode
    kbd.send_report(_report)
    time.sleep(KEY_HOLD)

    # 3. Release primary key but keep modifier active momentarily
    _report[2] = 0
    kbd.send_report(_report)
    time.sleep(0.005)

    # 4. Clean release of all keys
    if mod:
        _report[0] = 0
        kbd.send_report(_EMPTY)

KEY_ENTER = 0x28
KEY_SPACE = 0x2C

def _build_keymap():
    km = {}
    # a-z
    for i in range(26):
        km[chr(0x61 + i)] = (0, 0x04 + i)
    # A-Z
    for i in range(26):
        km[chr(0x41 + i)] = (MOD_LSHIFT, 0x04 + i)
    # 1-9
    for i in range(1, 10):
        km[chr(0x30 + i)] = (0, 0x1D + i)
    # 0
    km['0'] = (0, 0x27)
    # Space, Enter
    km[' ']  = (0, KEY_SPACE)
    km['\n'] = (0, KEY_ENTER)
    km['\t'] = (0, 0x2B)
    # Unshifted symbols
    for ch, kc in [
        ('-', 0x2D), ('=', 0x2E), ('[', 0x2F), (']', 0x30),
        ('\\',0x31), (';', 0x33), ("'", 0x34), ('`', 0x35),
        (',', 0x36), ('.', 0x37), ('/', 0x38),
    ]:
        km[ch] = (0, kc)
    # Shifted symbols
    for ch, kc in [
        ('!', 0x1E), ('@', 0x1F), ('#', 0x20), ('$', 0x21),
        ('%', 0x22), ('^', 0x23), ('&', 0x24), ('*', 0x25),
        ('(', 0x26), (')', 0x27), ('_', 0x2D), ('+', 0x2E),
        ('{', 0x2F), ('}', 0x30), ('|', 0x31), (':', 0x33),
        ('"', 0x34), ('~', 0x35), ('<', 0x36), ('>', 0x37),
        ('?', 0x38),
    ]:
        km[ch] = (MOD_LSHIFT, kc)
    return km

KEYMAP = _build_keymap()


def type_char(ch):
    entry = KEYMAP.get(ch)
    if entry is None:
        return                 # skip unmappable characters
    _press(entry[0], entry[1])
    time.sleep(CHAR_DELAY)

def press_enter():
    _press(0, KEY_ENTER)
    time.sleep(LINE_DELAY)

def type_program(path):
    with open(path, "r") as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        text = line.rstrip("\r\n")
        
        if text:
            for ch in text:
                type_char(ch)
                
        press_enter()
        if idx % 5 == 0:
            led.value = not led.value

    led.value = False

blink(int(STARTUP_DELAY), on=0.4, off=0.6)

led.value = True
type_program("/program.txt")
led.value = False

time.sleep(0.5)
blink(3, on=0.3, off=0.3)
