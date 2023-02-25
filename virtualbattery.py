from gi.repository import GLib
import logging
import sys
import os
import dbus
# from settings import *
from datetime import datetime as dt         # for UTC time stamps for logging
import time as tt                           # for charge measurement
import requests
import json

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('/opt/victronenergy/dbus-systemcalc-py/ext/velib_python')
from vedbus import VeDbusService #, VeDbusItemImport

class DbusVirtualBatService(object):
    
    def __init__(self, servicename='com.victronenergy.battery.virtual'):
        self._dbusservice = VeDbusService(servicename)
        self._dbusConn = dbus.SessionBus()  if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()
        
        # Create the mandatory objects
        self._dbusservice.add_mandatory_paths(processname = __file__, processversion = '0.0', connection = 'Virtual',
			deviceinstance = 15, productid = 0, productname = 'VirtualBattery', firmwareversion = 0.1, 
            hardwareversion = '0.0', connected = 1)

        # Create DC paths        
        self._dbusservice.add_path('/Dc/0/Voltage', None, writeable=True, gettextcallback=lambda a, x: "{:.2f}V".format(x))
        self._dbusservice.add_path('/Dc/0/Current', None, writeable=True, gettextcallback=lambda a, x: "{:.1f}A".format(x))
        self._dbusservice.add_path('/Dc/0/Power', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}W".format(x))
        
        # Create capacity paths
        self._dbusservice.add_path('/Soc', None, writeable=True)
        # self._dbusservice.add_path('/Capacity', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        # self._dbusservice.add_path('/InstalledCapacity', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        # self._dbusservice.add_path('/ConsumedAmphours', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        
        # Create temperature paths
        # self._dbusservice.add_path('/Dc/0/Temperature', None, writeable=True)       
        self._dbusservice.add_path('/System/MinCellTemperature', None, writeable=True)
        self._dbusservice.add_path('/System/MaxCellTemperature', None, writeable=True)
        # self._dbusservice.add_path('/System/MaxTemperatureCellId', None, writeable=True)       
        # self._dbusservice.add_path('/System/MinTemperatureCellId', None, writeable=True)
        
        # Create extras paths
        self._dbusservice.add_path('/System/MinCellVoltage', None, writeable=True)
        # self._dbusservice.add_path('/System/MinVoltageCellId', None, writeable=True)
        self._dbusservice.add_path('/System/MaxCellVoltage', None, writeable=True)
        # self._dbusservice.add_path('/System/MaxVoltageCellId', None, writeable=True)
        # self._dbusservice.add_path('/System/NrOfCellsPerBattery', None, writeable=True)
        # self._dbusservice.add_path('/System/NrOfModulesOnline', None, writeable=True)
        # self._dbusservice.add_path('/System/NrOfModulesOffline', None, writeable=True)
        # self._dbusservice.add_path('/System/NrOfModulesBlockingCharge', None, writeable=True)
        # self._dbusservice.add_path('/System/NrOfModulesBlockingDischarge', None, writeable=True)         
        
        # Create alarm paths
        # self._dbusservice.add_path('/Alarms/LowVoltage', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighVoltage', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowCellVoltage', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowSoc', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighChargeCurrent', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighDischargeCurrent', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/CellImbalance', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/InternalFailure', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighChargeTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowChargeTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowTemperature', None, writeable=True)
        #self._dbusservice.add_path('/Alarms/HighCellVoltage', None, writeable=True)
        
        # Create control paths
        self._dbusservice.add_path('/Info/MaxChargeCurrent', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxDischargeCurrent', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxChargeVoltage', None, writeable=True, gettextcallback=lambda a, x: "{:.1f}V".format(x))

        GLib.timeout_add(1000, self._update)    
    
    
    def _update(self):  

        
        try:
            
            r = requests.get('https://localhost:1881/virtualbattery', verify=False)

            json = r.json()

            #logging.info(f'{dt.now()} data received: {json}')
            
            with self._dbusservice as bus:
            
                bus['/Dc/0/Voltage'] = round(json['Voltage'], 2)
                bus['/Dc/0/Current'] = round(json['Current'], 2)
                bus['/Dc/0/Power'] = round(json['Power'], 0)
            
                bus['/Soc'] = json['Soc']
                # bus['/Capacity'] = Capacity
                # bus['/InstalledCapacity'] = InstalledCapacity
                # bus['/ConsumedAmphours'] = ConsumedAmphours
            
                # bus['/Dc/0/Temperature'] = Temperature
                bus['/System/MaxCellTemperature'] = json['MaxCellTemperature']
                bus['/System/MinCellTemperature'] = json['MinCellTemperature']
            
                bus['/System/MaxCellVoltage'] = json['MaxCellVoltage']
                # bus['/System/MaxVoltageCellId'] = MaxVoltageCellId
                bus['/System/MinCellVoltage'] = json['MinCellVoltage']
                # bus['/System/MinVoltageCellId'] = MinVoltageCellId
            
                # bus['/System/NrOfCellsPerBattery'] = NrOfCellsPerBattery
                # bus['/System/NrOfModulesOnline'] = NrOfModulesOnline
                # bus['/System/NrOfModulesOffline'] = NrOfModulesOffline
                # bus['/System/NrOfModulesBlockingCharge'] = NrOfModulesBlockingCharge
                # bus['/System/NrOfModulesBlockingDischarge'] = NrOfModulesBlockingDischarge
            
                # bus['/Alarms/LowVoltage'] = LowVoltage_alarm
                # bus['/Alarms/HighVoltage'] = HighVoltage_alarm
                # bus['/Alarms/LowCellVoltage'] = LowCellVoltage_alarm
                # bus['/Alarms/LowSoc'] = LowSoc_alarm
                # bus['/Alarms/HighChargeCurrent'] = HighChargeCurrent_alarm
                # bus['/Alarms/HighDischargeCurrent'] = HighDischargeCurrent_alarm
                # bus['/Alarms/CellImbalance'] = CellImbalance_alarm
                # bus['/Alarms/InternalFailure'] = InternalFailure_alarm
                # bus['/Alarms/HighChargeTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowChargeTemperature'] = LowChargeTemperature_alarm
                # bus['/Alarms/HighTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowTemperature'] = LowChargeTemperature_alarm
            
                bus['/Info/MaxChargeCurrent'] = json['MaxChargeCurrent']
                bus['/Info/MaxDischargeCurrent'] = json['MaxDischargeCurrent']
                bus['/Info/MaxChargeVoltage'] = json['MaxChargeVoltage']
        except Exception as e:
            logging.info(f'{dt.now()}:{e}, error occurred during update, retrying..')
            #GLib.timeout_add(5000, self._update) 

        return True
    
def main():
    logging.basicConfig(filename = 'virtualbattery.log', level=logging.INFO)

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    DbusVirtualBatService()

    logging.info(f'{dt.now()} Connected to dbus')

    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == "__main__":
    main()

