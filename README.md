# Pi Pico → Switch 2 SmileBASIC Auto-Typer

Automatically types text and bootstrap programs directly into SmileBASIC on the Switch 2 via low-level USB keyboard emulation.

---

## What You Need

| Item | Notes |
|---|---|
| **Raspberry Pi Pico** (RP2040 or RP2350) | Any standard Pico board |
| **USB Cable** | Data-capable cable (Micro-USB or USB-C depending on Pico version) |
| **Switch Dock** | Connect to one of the dock's **USB-A ports** (recommended over USB-C OTG) |
| **CircuitPython 9.x** | Standard board firmware from circuitpython.org |

---

## Setup Steps

### 1. Install CircuitPython on the Pico

1. Hold the **BOOTSEL** button while plugging the Pico into your PC.
2. Download the CircuitPython `.uf2` for your board from [circuitpython.org/downloads](https://circuitpython.org/downloads).
3. Drag and drop the `.uf2` file onto the **RPI-RP2** drive. The board will automatically reboot and mount as **CIRCUITPY**.

### 2. Copy Project Files

Copy these three files directly to the root of the **CIRCUITPY** drive:

```text
CIRCUITPY/
├── boot.py          ← Configures pure HID Boot Keyboard & hides storage/serial
├── code.py          ← Main auto-typer script (raw 8-byte HID reports)
└── program.txt      ← Target SmileBASIC program source to type
```

### 3. Plug into the Switch 2

1. Make sure your Switch 2 is docked.
2. Launch **SmileBASIC**.
3. Select an empty slot (e.g., `SLOT 0`, `1`, `2`, or `3`).
4. **Important**: Tap/click into the **Edit Mode** code editor area so the cursor is actively blinking inside the editor (not in the Direct Mode console at the bottom).
5. Plug the Pico into one of the **Switch Dock USB-A ports**.
6. The onboard LED will blink for 5 seconds as a startup countdown.
7. Typing will begin automatically. The onboard LED toggles every 10 lines as a progress indicator, followed by a triple blink when finished.

---

## Executing in Direct Mode

After the auto-typer finishes typing, switch to **Direct Mode** (press `F4` or tap the bottom console bar):

1. **Initialize the arrays:**
   ```basic
   RUN
   ```
   *(Displays `DIST BOOT READY 1015`)*

2. **Trigger the memory corruption primitive:**
   ```basic
   REMOVE NSR,&H60000000,&H3FFFFFFF
   ```
   > [!NOTE]
   > SmileBASIC will display `Out of memory`. This error is **normal and expected** — it indicates the integer overflow bypassed bounds checking. Enter this command only once per session.

3. **Launch the network connection / host RPC:**
   From your PC running your host listener/runner, enter the generated start command in Direct Mode:
   ```basic
   V=START(...)
   ```

---

## How It Works

```
┌─────────────────┐      Raw USB HID       ┌──────────────────┐
│  Raspberry Pi   │  Boot Keyboard Reports  │  Nintendo Switch │
│      Pico       │ ──────────────────────► │  (Docked USB-A)  │
│                 │      (Report ID 0)      │                  │
│ • boot.py       │                         │ • SmileBASIC     │
│ • code.py       │                         │   Editor receives│
│ • program.txt   │                         │   keystrokes     │
└─────────────────┘                         └──────────────────┘
```

Standard CircuitPython uses composite USB devices (Mass Storage + CDC Serial + HID) with Report ID prefixes (`adafruit_hid`), which game consoles ignore or reject.

This implementation overcomes those limitations:
1. **`boot.py`** strips away the mass storage and CDC serial interfaces, identifies the board as a standard generic `"USB Keyboard"`, and registers an official USB HID Boot Keyboard descriptor (USB HID Specification Appendix B.1).
2. **`report_ids=(0,)`** ensures keystrokes are transmitted as raw 8-byte packets without any prefix byte, exactly matching a physical hardware USB keyboard.
3. **`code.py`** reads `program.txt` and converts ASCII characters to HID modifier and scan-code pairs on the fly without relying on external dependencies.

---

## Tuning Typing Delays

You can adjust timing constants at the top of [code.py](file:///C:/Users/BrenK/.gemini/antigravity/scratch/pico-switch2-typer/code.py):

| Constant | Default | Purpose |
|---|---|---|
| `STARTUP_DELAY` | `5.0` s | Countdown delay before typing starts |
| `KEY_HOLD` | `0.025` s (25ms) | Key-down duration to guarantee host USB poll capture (>16.6ms) |
| `CHAR_DELAY` | `0.045` s (45ms) | Cooldown between distinct keystrokes |
| `LINE_DELAY` | `0.450` s (450ms) | Delay after pressing Enter to allow SmileBASIC time to parse each line |

---

## Modifying Files Later (Regaining Mass Storage Access)

Because `boot.py` disables mass storage so the Switch recognizes the keyboard, the `CIRCUITPY` drive will not mount normally when plugged into a PC.

To edit your files again:
1. Hold **BOOTSEL** on the Pico while plugging it into your PC.
2. Drag and drop a reset `.uf2` file onto the mounted **RPI-RP2** drive.
3. Continue from starting setup
