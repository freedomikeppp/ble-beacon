#-*- coding: utf-8 -*-
import asyncio
import multiprocessing as mp
from multiprocessing import Process, Manager
import platform
import sys
import threading
import tkinter as tk
import tkinter.messagebox as tkm

# macOS
if platform.system() == "Darwin":
    from bleak import discover
# Windows10
else:
    from bleak.backends.dotnet.discovery import discover

class RssiManager():

    data = {
        'RED': [],
        'BLUE': [],
        'YELLOW': [],
        'GREEN': [],
        'PURPLE': [],
        'WHITE': []
    }

    def insert_rssi(self, color, rssi):
        past_list = self.data.get(color)
        if(len(past_list) <= 10):
            past_list.append(int(rssi))
        else:
            past_list.append(int(rssi))
            past_list.pop(0)

    def get_average(self, color):
        past_list = self.data.get(color)
        total = 0
        for v in past_list:
            total += v
        return total / len(past_list)

class Beacon():

    # UUID is for macOS
    uuid_dic = {
        '0FEC7C6F-F05D-49AF-956A-CA08B413839F': 'RED',
        'FE1F23B9-6794-437E-B8C9-7A9D31616636': 'BLUE',
        '8F16E228-2BA6-4440-8CC4-6BD300EB5FB3': 'YELLOW',
        '': 'GREEN',
        '': 'PURPLE',
        '': 'WHITE'
    }
    # MAC Adress is for Windows10
    mac_dic = {
        'AC:23:3F:26:45:15': 'RED',
        'AC:23:3F:26:40:5B': 'BLUE',
        'AC:23:3F:26:40:48': 'YELLOW',
        '': 'GREEN',
        '': 'PURPLE',
        '': 'WHITE'
    }

    @classmethod
    def find(cls, key):
        if platform.system() == "Darwin":
            return cls.uuid_dic.get(key) if key in cls.uuid_dic.keys() else None
        else:
            return cls.mac_dic.get(key) if key in cls.mac_dic.keys() else None

    

def do_task(async_loop, master=None):
    '''非同期タスクの実行

    Args:
        async_loop (asyncio): asyncイベントループ
    '''
    threading.Thread(target=_asyncio_thread, args=(async_loop, master)).start()

def _asyncio_thread(async_loop, master):
    async_loop.run_until_complete(run_getting_packets(master))

async def run_getting_packets(master=None):
    '''Bluetoothモジュールを使いアドバタイズパケットを取得する。

    取得対象は、macOSの場合は'UUID'を、Windows10の場合は'MAC Address'で判定する。
    '''
    rssi_manager = RssiManager()
    count = 0
    while True:
        devices = await discover()
        count += 1
        for d in devices:
            color = Beacon.find(str(d).rsplit(':', 1)[0])
            if color is not None:
                print('UUID:', d)
                print('address:', d.address)
                print('details:', d.details)
                print('metadata:', d.metadata)
                print('name:', d.name)
                print('rssi:', d.rssi)
                if color == 'RED':
                    rssi_manager.insert_rssi('RED', d.rssi)
                    master.text1.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(rssi_manager.get_average('RED')) + 'dBm\n'
                    )
                elif color == 'BLUE':
                    rssi_manager.insert_rssi('BLUE', d.rssi)
                    master.text2.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(rssi_manager.get_average('BLUE')) + 'dBm\n'
                    )
                elif color == 'YELLOW':
                    rssi_manager.insert_rssi('YELLOW', d.rssi)
                    master.text3.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(rssi_manager.get_average('YELLOW')) + 'dBm\n'
                    )
        print('-----------------------------')

class MainFrame(tk.Frame):

    def __init__(self, master=None, async_loop=None):
        super().__init__(master)
        self.async_loop = async_loop
        self.master.title(u'BLE-Beacon Test')
        self.master.resizable(False, False)
        self.master['padx'] = 5
        self.master['pady'] = 5
        self.create_widgets()

        # Bug fixes for macOS
        self.master.update()
        self.master.after(0, self.fix)

    def create_widgets(self):
        self.label1 = tk.Label(text='Beacon RED', fg='red')
        self.label1.grid(row=0)
        self.label1['pady'] = 5
        self.text1 = tk.Text(width=50, height=10)
        self.text1.grid(row=1)
        self.text1['pady'] = 5

        self.label2 = tk.Label(text='Beacon BLUE', fg='blue')
        self.label2.grid(row=2)
        self.label2['pady'] = 5
        self.text2 = tk.Text(width=50, height=10)
        self.text2.grid(row=3)
        self.text2['pady'] = 5

        self.label3 = tk.Label(text='Beacon YELLOW', fg='yellow')
        self.label3.grid(row=4)
        self.label3['pady'] = 5
        self.text3 = tk.Text(width=50, height=10)
        self.text3.grid(row=5)
        self.text3['pady'] = 5

        self.label4 = tk.Label(text='Beacon GREEN', fg='green')
        self.label4.grid(row=0, column=1)
        self.label4['pady'] = 5
        self.text4 = tk.Text(width=50, height=10)
        self.text4.grid(row=1, column=1)
        self.text4['pady'] = 5

        self.label5 = tk.Label(text='Beacon PURPLE', fg='purple')
        self.label5.grid(row=2, column=1)
        self.label5['pady'] = 5
        self.text5 = tk.Text(width=50, height=10)
        self.text5.grid(row=3, column=1)
        self.text5['pady'] = 5

        self.label6 = tk.Label(text='Beacon WHITE', fg='gray')
        self.label6.grid(row=4, column=1)
        self.label6['pady'] = 5
        self.text6 = tk.Text(width=50, height=10)
        self.text6.grid(row=5, column=1)
        self.text6['pady'] = 5

        self.get_btn = tk.Button(text='Get packets', fg='black', command= lambda:do_task(async_loop, self))
        self.get_btn.grid(row=6)
        self.get_btn['pady'] = 5

        self.reset_btn = tk.Button(text='Reset logs', fg='black')
        self.reset_btn.bind("<Button-1>", self.delete_text)
        self.reset_btn.grid(row=6, column=1)
        self.reset_btn['pady'] = 5

    def fix(self):
        a = self.master.winfo_geometry().split('+')[0]
        b = a.split('x')
        w = int(b[0])
        h = int(b[1])
        self.master.geometry('%dx%d' % (w+1,h+1))

    def delete_text(self, event):
        self.text1.delete(1.0, tk.END)
        self.text2.delete(1.0, tk.END)
        self.text3.delete(1.0, tk.END)


def main(async_loop):
    root = tk.Tk()
    app = MainFrame(master=root, async_loop=async_loop)
    app.mainloop()

if __name__ == "__main__":
    async_loop = asyncio.get_event_loop()
    main(async_loop)
    