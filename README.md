# Victron virtual battery

this is a dbus service for the Victron venus OS. it is a virtual battery that doesn't do anything besides being available as a real battery in de venus OS. this is the only way to make sure that Venus OS and al its connected devices will honor the settings and information that this battery sends.

The idea behind this is that when you have a virtual battery available in Venus OS that it can be configured as the default battery. after that you are able to write data to it from any device (multiplusses, one or more BMS'es, smartshunts, etc.). when the information is stored in the virtual battery Venus OS will take care of the rest (making sure all chargers/devices receive the correct information and behave correctly) 

You can write data to the virtual battery using node-red with the Venus OS Large image. 

## Node-red

node-red gives you the option to read/extract information from all kinds of devices available on the dbus or from anywhere else. that information can be transformed/aggregated in any form and can be used to execute several actions (such as writing the right information to the virtual battery). A few ideas:

- Use cell voltages read from a specific BMS that you are using
- Use SOC readings from a victron smartshunt (higher accuracy)
- Use Amp reading from the multiplus itself, a specific BMS or a smartshunt

This way you have full control over how and which information flows through the system. You are also able to create your own logic rules, such as; 

- When one cell voltage is to high, lower max charge current
- When one cell voltage is to low, lower discharge current
- When temp is to high or to low, disable ... 
- When SOC is between 80 a 90%, set charge current to..
- When season is winter; maintain a specific SOC, when season is summer don't.
- Change max charge voltage to a higher value when SOC is above 95% for a fixed amount of time
- Etc.

## Example flow

...

## How to - CerboGX

Installation:
- create /data/dbus-virtual-battery directory
- copy the stuff into it
- set chmod 744 for ./service/run and ./restart
- add command ln -s /data/dbus-virtual-battery/service /service/dbus-virtual-battery into /data/rc.local

Configuration:
- make sure you have enabled modbus over TCP, this is needed for writing new data to the virtual battery

## How to - Node-red

- install this extra package from the node-red palette: ..........



The service starts automatically after start/restart of the Venus OS. After changing of aggregatebatteries.py or
settings.py restart it by executing:

./restart - it kills the service which starts automatically again.

For debugging (to see the error messages in the console) it could be reasonable to rename: ./service/run 
and start by: python3 aggregatebatteries.py

### Defaults

All default values can be changed from within the node-red ui. 


	
The max. charge voltage is either set to (CHARGE_VOLTAGE * Nr. of cells) or is limited to the immediate battery voltage if the first cell reaches 
the MAX_CELL_VOLTAGE. This avoids emergency disconnecting the battery by its BMS.    
	
The MaxChargeCurrent is reduced from MAX_CHARGE_CURRENT to MAX_CHARGE_CURRENT_ABOVE_CV1 when the first cell reaches CV1 and further
reduced to MAX_CHARGE_CURRENT_ABOVE_CV2 when the first cell reaches CV2.

The MaxDischargeCurrent is reduced from MAX_DISCHARGE_CURRENT to zero if the battery voltage falls down to (DISCHARGE_VOLTAGE * Nr. of cells)
or the first cell falls down to MIN_CELL_VOLTAGE.

The charge or discharge current is set to zero if at least one BMS is blocking charge or discharge respectively.

Logging file:
./service/aggregatebatteries.log	

Known issue:
- the last data from dbus-serialbattery driver remain on Dbus if the connection is interrupted. Therefore my software cannot recognize it as well.
