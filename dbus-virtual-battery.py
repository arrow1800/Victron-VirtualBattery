
from gi.repository import GLib
import logging
import sys
import os
import dbus
from datetime import datetime as dt         # for UTC time stamps for logging
import time                                 # for charge measurement
import requests
import json
from mqttclient import VictronMQTTClient

sys.path.append('/opt/victronenergy/dbus-systemcalc-py/ext/velib_python')
from vedbus import VeDbusService  # , VeDbusItemImport

class DbusVirtualBatService(object):

    lastMessage = time.time()
    timeoutInSeconds = None

    def __init__(self, timeout, servicename='com.victronenergy.battery.virtual'):
        self.timeoutInSeconds = timeout
        self._dbusservice = VeDbusService(servicename)
        self._dbusConn = dbus.SessionBus(
        ) if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()

        # Create the mandatory objects
        self._dbusservice.add_mandatory_paths(processname=__file__, processversion='0.0', connection='Virtual',
                                              deviceinstance=15, productid=0, productname='VirtualBattery MQTT', firmwareversion=0.1,
                                              hardwareversion='0.0', connected=1)

        # Create DC paths
        self._dbusservice.add_path(
            '/Dc/0/Voltage', None, writeable=True, gettextcallback=lambda a, x: "{:.2f}V".format(x))
        self._dbusservice.add_path(
            '/Dc/0/Current', None, writeable=True, gettextcallback=lambda a, x: "{:.1f}A".format(x))
        self._dbusservice.add_path(
            '/Dc/0/Power', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}W".format(x))

        # Create capacity paths
        self._dbusservice.add_path('/Soc', None, writeable=True)
        # self._dbusservice.add_path('/Capacity', None, writeable=True, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        # self._dbusservice.add_path('/InstalledCapacity', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))
        # self._dbusservice.add_path('/ConsumedAmphours', None, gettextcallback=lambda a, x: "{:.0f}Ah".format(x))

        # Create temperature paths
        # self._dbusservice.add_path('/Dc/0/Temperature', None, writeable=True)
        self._dbusservice.add_path(
            '/System/MinCellTemperature', None, writeable=True)
        self._dbusservice.add_path(
            '/System/MaxCellTemperature', None, writeable=True)
        # self._dbusservice.add_path('/System/MaxTemperatureCellId', None, writeable=True)
        # self._dbusservice.add_path('/System/MinTemperatureCellId', None, writeable=True)

        # Create extras paths
        self._dbusservice.add_path(
            '/System/MinCellVoltage', None, writeable=True)
        # self._dbusservice.add_path('/System/MinVoltageCellId', None, writeable=True)
        self._dbusservice.add_path(
            '/System/MaxCellVoltage', None, writeable=True)
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
        self._dbusservice.add_path(
            '/Alarms/InternalFailure', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighChargeTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowChargeTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/HighTemperature', None, writeable=True)
        # self._dbusservice.add_path('/Alarms/LowTemperature', None, writeable=True)
        #self._dbusservice.add_path('/Alarms/HighCellVoltage', None, writeable=True)

        # Create control paths
        self._dbusservice.add_path('/Info/MaxChargeCurrent', None,
                                   writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxDischargeCurrent', None,
                                   writeable=True, gettextcallback=lambda a, x: "{:.0f}A".format(x))
        self._dbusservice.add_path('/Info/MaxChargeVoltage', None,
                                   writeable=True, gettextcallback=lambda a, x: "{:.1f}V".format(x))

    def checkLastMessage(self):
        if (time.time() - self.lastMessage > self.timeoutInSeconds):
            logging.info(
                f'{dt.now()} Timeout on MQTT message. Setting failsafe...')
            # print(f'{dt.now()} Timeout on MQTT message. Setting failsafe...')
            self.setFailsafeSettings()
        return True

    def setFailsafeSettings(self):
        '''construct custom json obj
        call update manually
        '''

        #json string data
        data = '''{
        "Voltage": 53.8, 
        "Current": 0, 
        "Power": 0,
        "Soc" : 0,
        "MaxCellTemperature" : 0,
        "MinCellTemperature" : 0,
        "MaxCellVoltage" : 3.65,
        "MinCellVoltage" : 2.70,
        "InternalFailure" : 1,
        "MaxChargeCurrent" : 0,
        "MaxDischargeCurrent" : 0,
        "MaxChargeVoltage" : 53.8
        }'''

        data = json.loads(data)

        self._update(data)

    def callback(self, client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        data = json.loads(msg.payload)

        # in case we receive data we set this to 0
        data['InternalFailure'] = 0

        self._update(data)

    def _update(self, data):

        try:

            # logging.info(f'received data: {data}')
            # print(f'received data: {data}')

            with self._dbusservice as bus:

                bus['/Dc/0/Voltage'] = round(data.get('Voltage'), 2)
                bus['/Dc/0/Current'] = round(data.get('Current'), 2)
                bus['/Dc/0/Power'] = round(data.get('Power'), 0)

                bus['/Soc'] = data.get('Soc')
                # bus['/Capacity'] = Capacity
                # bus['/InstalledCapacity'] = InstalledCapacity
                # bus['/ConsumedAmphours'] = ConsumedAmphours

                # bus['/Dc/0/Temperature'] = Temperature
                bus['/System/MaxCellTemperature'] = data.get(
                    'MaxCellTemperature')
                bus['/System/MinCellTemperature'] = data.get(
                    'MinCellTemperature')

                bus['/System/MaxCellVoltage'] = data.get('MaxCellVoltage')
                # bus['/System/MaxVoltageCellId'] = MaxVoltageCellId
                bus['/System/MinCellVoltage'] = data.get('MinCellVoltage')
                # bus['/System/MinVoltageCellId'] = MinVoltageCellId

                # bus['/System/NrOfCellsPerBattery'] = NrOfCellsPerBattery
                # bus['/System/NrOfModulesOnline'] = NrOfModulesOnline
                # bus['/System/NrOfModulesOffline'] = NrOfModulesOffline
                # bus['/System/NrOfModulesBlockingCharge'] = data.get('ModulesBlockingCharge')
                # bus['/System/NrOfModulesBlockingDischarge'] = NrOfModulesBlockingDischarge

                # bus['/Alarms/LowVoltage'] = LowVoltage_alarm
                # bus['/Alarms/HighVoltage'] = HighVoltage_alarm
                # bus['/Alarms/LowCellVoltage'] = LowCellVoltage_alarm
                # bus['/Alarms/LowSoc'] = LowSoc_alarm
                # bus['/Alarms/HighChargeCurrent'] = HighChargeCurrent_alarm
                # bus['/Alarms/HighDischargeCurrent'] = HighDischargeCurrent_alarm
                # bus['/Alarms/CellImbalance'] = CellImbalance_alarm
                bus['/Alarms/InternalFailure'] = data.get('InternalFailure')

                # bus['/Alarms/HighChargeTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowChargeTemperature'] = LowChargeTemperature_alarm
                # bus['/Alarms/HighTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowTemperature'] = LowChargeTemperature_alarm

                bus['/Info/MaxChargeCurrent'] = data.get('MaxChargeCurrent')
                bus['/Info/MaxDischargeCurrent'] = data.get(
                    'MaxDischargeCurrent')
                bus['/Info/MaxChargeVoltage'] = data.get('MaxChargeVoltage')

                self.lastMessage = time.time()

                
        except Exception as e:
            logging.info(
                f'{dt.now()}:{e}, error occurred during update, retrying..')
            # print(f'{dt.now()}:{e}, error occurred during update, retrying..')
            # self.setFailsafeSettings()

        return True


def main():
    logging.basicConfig(filename='virtualbattery.log', level=logging.INFO)
    
    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    
    customService = DbusVirtualBatService(60)

    logging.info(f'{dt.now()} Connected to dbus')

    # Configuration MQTT
    client = VictronMQTTClient(
        'localhost', 1883, 'virtualbattery', customService.callback)
    client.start()

    GLib.timeout_add_seconds(customService.timeoutInSeconds, customService.checkLastMessage)

    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
