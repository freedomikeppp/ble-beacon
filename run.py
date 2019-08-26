#-*- coding: utf-8 -*-
import platform
import pprint
import re
import sys
import tkinter as tk
import tkinter.messagebox as tkm

# --------------- tkinter ---------------
# root = tk.Tk()
# root.title(u'BLE-Beacon Test')
# root.geometry('800x400')
# root.mainloop()

# --------------- get bluetoothe devices ---------------


# '0FEC7C6F-F05D-49AF-956A-CA08B413839F', # Red
# 'ac:23:3f:26:45:15', 
# '8F16E228-2BA6-4440-8CC4-6BD300EB5FB3', # Yellow
# 'ac:23:3f:26:40:48',
# 'FE1F23B9-6794-437E-B8C9-7A9D31616636', # Blue
# 'ac:23:3f:26:40:5b'

import asyncio
from bleak import BleakClient

address = "0FEC7C6F-F05D-49AF-956A-CA08B413839F"
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

async def run(address, loop):
    async with BleakClient(address, loop=loop) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))