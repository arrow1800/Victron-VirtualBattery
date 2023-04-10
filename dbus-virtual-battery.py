
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

    def __init__(self, timeout, servicename='com.victronenergy.battery.virtual.test'):
        self.timeoutInSeconds = timeout
        self._dbusservice = VeDbusService(servicename)
        self._dbusConn = dbus.SessionBus(
        ) if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()

        # Create the mandatory objects
        self._dbusservice.add_mandatory_paths(processname=__file__, processversion='0.0', connection='Virtual',
                                              deviceinstance=19, productid=0, productname='VirtualBattery MQTT', firmwareversion=0.1,
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
        self._update(53.8, 'voltage')
        self._update(0, 'current')
        self._update(0, 'power')
        self._update(0, 'soc')
        self._update(0, 'maxCellTemperature')
        self._update(0, 'minCellTemperature')
        self._update(3.65, 'maxCellVoltage')
        self._update(2.70, 'minCellVoltage')
        self._update(1, 'internalFailure')
        self._update(0, 'maxChargeCurrent')
        self._update(0, 'maxDischargeCurrent')
        self._update(53.8, 'maxChargeVoltage')

    def callback(self, client, userdata, msg):
        
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        
        payload = float(msg.payload.decode())
        topic = msg.topic.replace('virtualbattery/', '')

        self._update(payload, topic)

    def _update(self, payload, topic):

        try:

            # logging.info(f'received data: {data}')
            # print(f'received data: {data}')

            with self._dbusservice as bus:

                if topic == 'voltage':
                    bus['/Dc/0/Voltage'] = payload

                if topic == 'current':
                    bus['/Dc/0/Current'] = payload

                if topic == 'power':
                    bus['/Dc/0/Power'] = payload

                if topic == 'soc':
                    bus['/Soc'] = payload

                if topic == 'maxCellTemperature':
                    bus['/System/MaxCellTemperature'] = payload

                if topic == 'minCellTemperature':
                    bus['/System/MinCellTemperature'] = payload

                if topic == 'maxCellVoltage':
                    bus['/System/MaxCellVoltage'] = payload

                if topic == 'minCellVoltage':
                    bus['/System/MinCellVoltage'] = payload

                if topic == 'maxChargeCurrent':
                    bus['/Info/MaxChargeCurrent'] = payload

                if topic == 'maxDischargeCurrent':
                    bus['/Info/MaxDischargeCurrent'] = payload
                
                if topic == 'maxChargeVoltage':
                    bus['/Info/MaxChargeVoltage'] = payload

                bus['/Alarms/InternalFailure'] = 0

                # bus['/Capacity'] = Capacity
                # bus['/InstalledCapacity'] = InstalledCapacity
                # bus['/ConsumedAmphours'] = ConsumedAmphours

                # bus['/Dc/0/Temperature'] = Temperature

                # bus['/System/MaxVoltageCellId'] = MaxVoltageCellId
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

                # bus['/Alarms/HighChargeTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowChargeTemperature'] = LowChargeTemperature_alarm
                # bus['/Alarms/HighTemperature'] = HighChargeTemperature_alarm
                # bus['/Alarms/LowTemperature'] = LowChargeTemperature_alarm

                self.lastMessage = time.time()

                print(f'{dt.now()} updated dbus')
                
        except Exception as e:
            logging.info(
                f'{dt.now()}:{e}, error occurred during update, retrying..')
            print(f'{dt.now()}:{e}, error occurred during update, retrying..')
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
        'localhost', 1883, 'virtualbattery/+', customService.callback)
    client.start()

    GLib.timeout_add_seconds(customService.timeoutInSeconds, customService.checkLastMessage)

    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
