"""
Service Explorer
----------------
An example showing how to access and print out the services, characteristics and
descriptors of a connected GATT server.
Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
"""
import platform
import asyncio
import logging

from bleak import BleakClient


async def run(address, loop, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        import sys

        loop.set_debug(True)
        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address, loop=loop) as client:
        x = await client.is_connected()
        log.info("Connected: {0}".format(x))

        for service in client.services:
            log.info("[Service] {0}: {1}".format(service.uuid, service.description))
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = None
                log.info(
                    "\t[Characteristic] {0}: ({1}) | Name: {2}, Value: {3} ".format(
                        char.uuid, ",".join(char.properties), char.description, value
                    )
                )
                for descriptor in char.descriptors:
                    value = await client.read_gatt_descriptor(descriptor.handle)
                    log.info(
                        "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                            descriptor.uuid, descriptor.handle, bytes(value)
                        )
                    )


if __name__ == "__main__":
    address = (
        "ac:23:3f:26:45:15" # using Windows or Linux
        if platform.system() != "Darwin"
        else "0FEC7C6F-F05D-49AF-956A-CA08B413839F" # using macOS
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop, True))