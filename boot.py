import supervisor
import usb_hid
import usb_cdc
import storage

storage.disable_usb_drive()
usb_cdc.disable()

supervisor.set_usb_identification(
    manufacturer="USB",
    product="Keyboard",
)

BOOT_KBD_DESC = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x06,        # Usage (Keyboard)
    0xA1, 0x01,        # Collection (Application)
    # Modifiers (8 bits)
    0x05, 0x07,        #   Usage Page (Keypad)
    0x19, 0xE0,        #   Usage Min (Left Ctrl)
    0x29, 0xE7,        #   Usage Max (Right GUI)
    0x15, 0x00,        #   Logical Min (0)
    0x25, 0x01,        #   Logical Max (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x81, 0x02,        #   Input (Data, Var, Abs)
    # Reserved padding byte
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x08,        #   Report Size (8)
    0x81, 0x01,        #   Input (Const)
    # LEDs (Output)
    0x95, 0x05,        #   Report Count (5)
    0x75, 0x01,        #   Report Size (1)
    0x05, 0x08,        #   Usage Page (LEDs)
    0x19, 0x01,        #   Usage Min (Num Lock)
    0x29, 0x05,        #   Usage Max (Kana)
    0x91, 0x02,        #   Output (Data, Var, Abs)
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x03,        #   Report Size (3)
    0x91, 0x01,        #   Output (Const)
    # Key array (6 concurrency slots)
    0x95, 0x06,        #   Report Count (6)
    0x75, 0x08,        #   Report Size (8)
    0x15, 0x00,        #   Logical Min (0)
    0x26, 0xFF, 0x00,  #   Logical Max (255)
    0x05, 0x07,        #   Usage Page (Keypad)
    0x19, 0x00,        #   Usage Min (0)
    0x2A, 0xFF, 0x00,  #   Usage Max (255)
    0x81, 0x00,        #   Input (Data, Array)
    0xC0               # End Collection
])

boot_kbd = usb_hid.Device(
    report_descriptor=BOOT_KBD_DESC,
    usage_page=0x01,       # Generic Desktop
    usage=0x06,            # Keyboard
    report_ids=(0,),       # Report ID 0 = no ID prefix byte (boot protocol)
    in_report_lengths=(8,),
    out_report_lengths=(1,),
)

usb_hid.enable((boot_kbd,), boot_device=1)
