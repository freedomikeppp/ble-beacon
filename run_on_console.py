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


class BeaconManager():
    '''ビーコンのUUID・MAC Address・RSSI値を管理するクラス。

    キーとなる文字列は、色（color）で管理する。
    '''
    beacons = {
        'RED': {
            'uuid': '0FEC7C6F-F05D-49AF-956A-CA08B413839F', # UUID is for macOS
            'mac_address': 'AC:23:3F:26:45:15', # MAC Adress is for Windows10
            'rssi_data': []
        },
        'BLUE': {
            'uuid': 'FE1F23B9-6794-437E-B8C9-7A9D31616636',
            'mac_address': 'AC:23:3F:26:40:5B',
            'rssi_data': []
        },
        'YELLOW': {
            'uuid': '8F16E228-2BA6-4440-8CC4-6BD300EB5FB3',
            'mac_address': 'AC:23:3F:26:40:48',
            'rssi_data': []
        }
    }

    @classmethod
    def find(cls, unique_id):
        '''UUID、またはMAC Addressから、ビーコン色を取得する。

        取得対象は、macOSの場合は'UUID'を、Windows10の場合は'MAC Address'で判定する。
        '''
        if platform.system() == "Darwin":
            for key_color in cls.beacons.keys():
                if unique_id in cls.beacons.get(key_color).get('uuid'):
                    return key_color
        else:
            for key_color in cls.beacons.keys():
                if unique_id in cls.beacons.get(key_color).get('mac_address'):
                    return key_color
        return None

    @classmethod
    def insert_rssi(cls, key_color, rssi):
        '''指定した色のRSSI値を登録し、最新の10件まで保存する。
        
        Args:
            key_color (str): 色
            rssi (int): RSSI値（電波の強さ）
        '''
        rssi_list = cls.beacons.get(key_color).get('rssi_data')
        if(len(rssi_list) <= 10):
            rssi_list.append(int(rssi))
        else:
            rssi_list.append(int(rssi))
            rssi_list.pop(0)

    @classmethod
    def get_average(cls, key_color):
        '''指定した色のRSSIの平均値を取得する。存在しない場合はNoneが返る。
        
        Args:
            key_color (str): 色
        Return:
            int: RSSI平均値。但し、存在しない場合は、None。
        '''
        rssi_list = cls.beacons.get(key_color).get('rssi_data')
        total = 0
        if len(rssi_list) > 0:
            for v in rssi_list:
                total += v
            return round(total / len(rssi_list), 2)
        else:
            return None

    @classmethod
    def get_nearest_beacon(cls):
        '''管理しているRSSI平均値の中で、一番大きな平均値値を持つ(一番距離が近い)ビーコン情報を返す。
        
        Return:
            dict: exp) {'key_color': 'RED', 'average_rssi': -48.3}
        '''
        beacon_dict = {}
        for key_color in cls.beacons.keys():
            average_rssi = cls.get_average(key_color)
            if len(beacon_dict) == 0 or (average_rssi is not None and beacon_dict.get('average_rssi') < average_rssi):
                beacon_dict = {
                    'key_color': key_color,
                    'average_rssi': average_rssi
                }
        return beacon_dict

    
def do_task(async_loop, master=None):
    '''非同期でビーコンを受信するタスクを開始する。'''
    if master.is_do_task == False:
        master.is_do_task = True
        threading.Thread(target=_asyncio_thread, args=(async_loop, master)).start()
    else:
        pass

def _asyncio_thread(async_loop, master):
    async_loop.run_until_complete(run_getting_packets(master))

async def run_getting_packets(master=None):
    '''Bluetoothモジュールを使いアドバタイズパケットを取得する'''
    count = 0
    while True:
        devices = await discover()
        count += 1
        for d in devices:
            key_color = BeaconManager.find(str(d).rsplit(':', 1)[0])
            if key_color is not None:
                # print('UUID:', d)
                # print('address:', d.address)
                # print('details:', d.details)
                # print('metadata:', d.metadata)
                # print('name:', d.name)
                # print('rssi:', d.rssi)
                if key_color == 'RED':
                    BeaconManager.insert_rssi('RED', d.rssi)
                    master.text1.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(BeaconManager.get_average('RED')) + 'dBm\n'
                    )
                elif key_color == 'BLUE':
                    BeaconManager.insert_rssi('BLUE', d.rssi)
                    master.text2.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(BeaconManager.get_average('BLUE')) + 'dBm\n'
                    )
                elif key_color == 'YELLOW':
                    BeaconManager.insert_rssi('YELLOW', d.rssi)
                    master.text3.insert(
                        1.0,
                        'seq: ' + str(count) + ', rssi: ' + str(d.rssi) + 'dBm, average: ' + str(BeaconManager.get_average('YELLOW')) + 'dBm\n'
                    )
        beacon_dic = BeaconManager.get_nearest_beacon()
        master.nearest_beacon_stringvar.set('The nearest beacon is the color of ' + beacon_dic.get('key_color') + ' (rssi: ' + str(beacon_dic.get('average_rssi')) + ')')
        master.nearest_beacon['fg'] = beacon_dic.get('key_color').lower()
        await asyncio.sleep(0.2)


class MainFrame(tk.Frame):

    def __init__(self, master=None, async_loop=None):
        super().__init__(master)
        self.async_loop = async_loop
        self.master.title(u'BLE-Beacon Test')
        self.master.resizable(False, False)
        self.master['padx'] = 5
        self.master['pady'] = 5
        self.create_widgets()
        self.is_do_task = False

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

        self.label6 = tk.Label(text='Beacon GRAY', fg='gray')
        self.label6.grid(row=4, column=1)
        self.label6['pady'] = 5
        self.text6 = tk.Text(width=50, height=10)
        self.text6.grid(row=5, column=1)
        self.text6['pady'] = 5
        
        self.nearest_beacon_stringvar = tk.StringVar()
        self.nearest_beacon_stringvar.set('The nearest beacon is nothing.')
        self.nearest_beacon = tk.Label(textvariable=self.nearest_beacon_stringvar, fg='black')
        self.nearest_beacon.grid(row=6, columnspan=2)
        self.nearest_beacon['pady'] = 5

        self.get_btn = tk.Button(text='Get packets', fg='black', command= lambda:do_task(async_loop, self))
        self.get_btn.grid(row=7)
        self.get_btn['pady'] = 5

        self.reset_btn = tk.Button(text='Reset logs', fg='black')
        self.reset_btn.bind("<Button-1>", self.delete_text)
        self.reset_btn.grid(row=7, column=1)
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
    