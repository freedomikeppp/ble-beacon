#-*- coding: utf-8 -*-
import asyncio
import platform
import sys

if platform.system() == "Darwin":
    from bleak import discover
else:
    from bleak.backends.dotnet.discovery import discover

# --------------- get bluetoothe devices ---------------
uuid_list = [
    '0FEC7C6F-F05D-49AF-956A-CA08B413839F', # Red
    'ac:23:3f:26:45:15', 
    '8F16E228-2BA6-4440-8CC4-6BD300EB5FB3', # Yellow
    'ac:23:3f:26:40:48',
    'FE1F23B9-6794-437E-B8C9-7A9D31616636', # Blue
    'ac:23:3f:26:40:5b'
]
async def run():
    while True:
        devices = await discover()
        for d in devices:
            print(d)
            if str(d).rsplit(':', 1)[0] in uuid_list:
                print('UUID:', d)
                print('address:', d.address)
                print('details:', d.details)
                print('metadata:', d.metadata)
                print('name:', d.name)
                print('rssi:', d.rssi)
        print('-----------------------------')
        await asyncio.sleep(1)
try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
finally:
    loop.close()
