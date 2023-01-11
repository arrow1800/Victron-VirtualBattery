"""
Service to create a virtual battery within the venus os
"""

VERSION = '0.1'

from gi.repository import GLib
import logging
import sys
import os
import dbus
from settings import *
from datetime import datetime as dt         # for UTC time stamps for logging
import time as tt                           # for charge measurement

sys.path.append('/opt/victronenergy/dbus-systemcalc-py/ext/velib_python')
from vedbus import VeDbusService, VeDbusItemImport

class DbusVirtualBatService(object):
    
    def __init__(self, servicename='com.victronenergy.battery.virtual'):
        # self._batteries = []
        # self._multi = None
        # self._mppts = []
        # self._scanTrials = 0
        # self._readTrials = 0
        # self._MaxChargeVoltage_old = 0
        # self._MaxChargeCurrent_old = 0
        # self._MaxDischargeCurrent_old = 0
        self._dbusservice = VeDbusService(servicename)
        self._dbusConn = dbus.SessionBus()  if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()
        # self._timeOld = tt.time() 
        
        # Create the mandatory objects
        self._dbusservice.add_mandatory_paths(processname = __file__, processversion = '0.0', connection = 'Virtual',
			deviceinstance = 0, productid = 0, productname = 'VirtualBattery', firmwareversion = VERSION, 
            hardwareversion = '0.0', connected = 1)

        # Create DC paths        
        self._dbusservice.add_path('/Dc/0/Voltage', None, writeable=True, gettextcallback=lambda a, x: "{:.2f}V".format(x))
        self._dbusservice.add_path('/Dc/0/Current', None, writeable=True, gettextcallback=lambda a, x: "{:.1f}A".format(x))
        self._dbusservice.add_path('/Dc/0/Power', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}W".format(x))
        
        # Create capacity paths
        self._dbusservice.add_path('/Soc', None, writeable=True)
        self._dbusservice.add_path('/Capacity', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        self._dbusservice.add_path('/InstalledCapacity', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        self._dbusservice.add_path('/ConsumedAmphours', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        
        # Create temperature paths
        self._dbusservice.add_path('/Dc/0/Temperature', None, writeable=True)       
        self._dbusservice.add_path('/System/MinCellTemperature', None, writeable=True)
        self._dbusservice.add_path('/System/MaxCellTemperature', None, writeable=True)

        #self._dbusservice.add_path('/System/MaxTemperatureCellId', None, writeable=True)       
        #self._dbusservice.add_path('/System/MinTemperatureCellId', None, writeable=True)
        
        # Create extras paths
        self._dbusservice.add_path('/System/MinCellVoltage', None, writeable=True)
        self._dbusservice.add_path('/System/MinVoltageCellId', None, writeable=True)
        self._dbusservice.add_path('/System/MaxCellVoltage', None, writeable=True)
        self._dbusservice.add_path('/System/MaxVoltageCellId', None, writeable=True)
        self._dbusservice.add_path('/System/NrOfCellsPerBattery', None, writeable=True)
        self._dbusservice.add_path('/System/NrOfModulesOnline', None, writeable=True)
        self._dbusservice.add_path('/System/NrOfModulesOffline', None, writeable=True)
        self._dbusservice.add_path('/System/NrOfModulesBlockingCharge', None, writeable=True)
        self._dbusservice.add_path('/System/NrOfModulesBlockingDischarge', None, writeable=True)         
        
        # Create alarm paths
        self._dbusservice.add_path('/Alarms/LowVoltage', None, writeable=True)
        self._dbusservice.add_path('/Alarms/HighVoltage', None, writeable=True)
        self._dbusservice.add_path('/Alarms/LowCellVoltage', None, writeable=True)
        self._dbusservice.add_path('/Alarms/LowSoc', None, writeable=True)
        self._dbusservice.add_path('/Alarms/HighChargeCurrent', None, writeable=True)
        self._dbusservice.add_path('/Alarms/HighDischargeCurrent', None, writeable=True)
        self._dbusservice.add_path('/Alarms/CellImbalance', None, writeable=True)
        self._dbusservice.add_path('/Alarms/InternalFailure', None, writeable=True)
        self._dbusservice.add_path('/Alarms/HighChargeTemperature', None, writeable=True)
        self._dbusservice.add_path('/Alarms/LowChargeTemperature', None, writeable=True)
        self._dbusservice.add_path('/Alarms/HighTemperature', None, writeable=True)
        self._dbusservice.add_path('/Alarms/LowTemperature', None, writeable=True)
        #self._dbusservice.add_path('/Alarms/HighCellVoltage', None, writeable=True)
        
        # Create control paths
        self._dbusservice.add_path('/Info/MaxChargeCurrent', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxDischargeCurrent', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxChargeVoltage', None, writeable=True, gettextcallback=lambda a, x: "{:.1f}V".format(x))
    
    
    #########################################    
    # update Dbus
    #########################################
    
    def _update(self):  
        
        # # DC
        # Voltage = 0
        # Current = 0
        # Power = 0
        
        # # Capacity
        # Soc = 0
        # Capacity = 0
        # InstalledCapacity = 0
        # ConsumedAmphours = 0        
        
        # # Temperature
        # Temperature = 0
        # MaxCellTemperature = []    
        # MinCellTemperature = []  
        
        # # Extras
        # MaxCellVoltage = {}         # dictionary {'ID' : MaxCellVoltage, ... } for all physical batteries
        # MinCellVoltage = {}         # dictionary {'ID' : MinCellVoltage, ... } for all physical batteries        
        # NrOfCellsPerBattery = []    # list, NRofCells of all physical batteries (shall be the same)
        # NrOfModulesOnline = 0
        # NrOfModulesOffline = 0
        # NrOfModulesBlockingCharge = 0
        # NrOfModulesBlockingDischarge = 0
        
        # # Alarms
        # LowVoltage_alarm = []       # lists to find maxima
        # HighVoltage_alarm = []
        # LowCellVoltage_alarm = []
        # #HighCellVoltage_alarm = []
        # LowSoc_alarm = []
        # HighChargeCurrent_alarm = []
        # HighDischargeCurrent_alarm = []
        # CellImbalance_alarm = []
        # InternalFailure_alarm = []
        # HighChargeTemperature_alarm = []
        # LowChargeTemperature_alarm = []
        # HighTemperature_alarm = []
        # LowTemperature_alarm = []

        # with self._dbusservice as bus:
        
        #     # send DC
        #     # bus['/Dc/0/Voltage'] = round(Voltage, 1)
        #     # bus['/Dc/0/Current'] = round(Current, 1)
        #     # bus['/Dc/0/Power'] = round(Power, 0)
        
        #     # send capacity
        #     bus['/Soc'] = Soc
        #     bus['/Capacity'] = Capacity
        #     bus['/InstalledCapacity'] = InstalledCapacity
        #     bus['/ConsumedAmphours'] = ConsumedAmphours
        
        #     # send temperature
        #     # bus['/Dc/0/Temperature'] = Temperature
        #     # bus['/System/MaxCellTemperature'] = MaxCellTemp
        #     # bus['/System/MinCellTemperature'] = MinCellTemp
        
        #     # send cell min/max voltage
        #     # bus['/System/MaxCellVoltage'] = MaxCellVoltage
        #     # bus['/System/MaxVoltageCellId'] = MaxVoltageCellId
        #     # bus['/System/MinCellVoltage'] = MinCellVoltage
        #     # bus['/System/MinVoltageCellId'] = MinVoltageCellId
        
        #     # send battery state
        #     bus['/System/NrOfCellsPerBattery'] = NrOfCellsPerBattery
        #     bus['/System/NrOfModulesOnline'] = NrOfModulesOnline
        #     bus['/System/NrOfModulesOffline'] = NrOfModulesOffline
        #     bus['/System/NrOfModulesBlockingCharge'] = NrOfModulesBlockingCharge
        #     bus['/System/NrOfModulesBlockingDischarge'] = NrOfModulesBlockingDischarge
        
        #     # send alarms
        #     bus['/Alarms/LowVoltage'] = LowVoltage_alarm
        #     bus['/Alarms/HighVoltage'] = HighVoltage_alarm
        #     bus['/Alarms/LowCellVoltage'] = LowCellVoltage_alarm
        #     #bus['/Alarms/HighCellVoltage'] = HighCellVoltage_alarm   # not implemended in Venus
        #     bus['/Alarms/LowSoc'] = LowSoc_alarm
        #     bus['/Alarms/HighChargeCurrent'] = HighChargeCurrent_alarm
        #     bus['/Alarms/HighDischargeCurrent'] = HighDischargeCurrent_alarm
        #     bus['/Alarms/CellImbalance'] = CellImbalance_alarm
        #     bus['/Alarms/InternalFailure'] = InternalFailure_alarm
        #     bus['/Alarms/HighChargeTemperature'] = HighChargeTemperature_alarm
        #     bus['/Alarms/LowChargeTemperature'] = LowChargeTemperature_alarm
        #     bus['/Alarms/HighTemperature'] = HighChargeTemperature_alarm
        #     bus['/Alarms/LowTemperature'] = LowChargeTemperature_alarm
        
        #     # send charge/discharge control
        #     bus['/Info/MaxChargeCurrent'] = MaxChargeCurrent
        #     bus['/Info/MaxDischargeCurrent'] = MaxDischargeCurrent
        #     bus['/Info/MaxChargeVoltage'] = MaxChargeVoltage

        return True
    
def main():
    logging.basicConfig(filename = 'aggregatebatteries.log', level=logging.INFO)

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    DbusAggBatService()
    logging.info('%s: Connected to dbus, and switching over to GLib.MainLoop() (= event based)' % dt.now())
    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == "__main__":
    main()

