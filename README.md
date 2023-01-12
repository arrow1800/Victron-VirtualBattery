# Victron virtual battery

this is a dbus service for the Victron venus OS. It is a virtual battery that doesn't do anything besides being available as a real battery in the venus OS. This is the only way to make sure that Venus OS and all its connected devices will honor the settings and information that this battery produces.

The idea behind this is that when you have a virtual battery available in Venus OS it can be configured as the default battery. after that you are able to write any combination of data to it from any device (multiplusses, one or more BMS'es, smartshunts, etc.). When the information is stored in the virtual battery Venus OS will take care of the rest (making sure all chargers/devices receive the correct information and behave accordingly) 

You can write data to the virtual battery using node-red with the Venus OS Large image. 

![screenshot of virtual battery in venus os](https://github.com/arrow1800/Victron-VirtualBattery/blob/main/img/virtualbattery-screenshot.png)
![screenshot of virtual battery in venus os](https://github.com/arrow1800/Victron-VirtualBattery/blob/main/img/virtualbattery-screenshot1.png)

## Node-red

node-red gives you the option to read/extract information from all kinds of devices available on the dbus or from anywhere else. That information can be transformed/aggregated in any form and can be used to execute several actions (such as writing the right information to the virtual battery). A few ideas:

- Use cell voltages read from one or more specific BMS'es that you are using
- Use SOC readings from a victron smartshunt (higher accuracy)
- Use Amps reading from the multiplus itself, a specific BMS or a smartshunt
- Any of the above in a combined way

This way you have full control over how and which information flows through the system. You are also able to create your own logic rules with node-red, such as; 

- When one cell voltage is to high, lower max charge current
- When one cell voltage is to low, lower discharge current
- When temp is to high or to low, disable ... 
- When SOC is between 80 a 90%, set charge current to..
- When season is winter; maintain a specific SOC, when season is summer don't.
- Change max charge voltage to a higher value when SOC is above 95% for a fixed amount of time
- Etc.

## Example flow

see file exampleflow.json you can copy the contents to node-red and import it all at once.

![screenshot of node-red flow](https://github.com/arrow1800/Victron-VirtualBattery/blob/main/img/node-red-screenshot.png)

## How to - CerboGX

Installation:
- create /data/dbus-virtual-battery directory
- copy files to this folder
- set chmod 744 for ./service/run and ./restart
- add this line to the file /data/rc.local : ln -s /data/dbus-virtual-battery/service /service/dbus-virtual-battery 


The service now starts automatically after a start/restart of the Venus OS

## Architecture

![virtual battery architecture](https://github.com/arrow1800/Victron-VirtualBattery/blob/main/img/architecture.png)

### Reading data

Reading data is done from within node-red. the most easiest way is using the default blue victron module nodes. 

### Sending data 

As can be seen in the architecture image. The virtual battery driver itself sends requests to a running REST api in node-red. Node-red replies with a response (including all virtual battery settings) which is then processed by the virtual battery itself (python file)

### Changing data

All properties (soc, voltage, etc) are stored in flow variables. when the battery driver sends a request to node-red, node-red retrieves all this variables and constructs a dictionary that is send back. this is done in the function block named: flow to dictionary

setting other max discharge values for example can be done by changing the current function blocks that are connected to the 'every second trigger' or just add new ones. make sure the result always ends up in one of the following flow variables:

```
let k1 = 'Soc'
let k2 = 'Current'
let k3 = 'Voltage'
let k4 = 'Power'
let k5 = 'MinCellTemperature'
let k6 = 'MaxCellTemperature'
let k7 = 'MaxChargeCurrent'
let k8 = 'MaxDischargeCurrent'
let k9 = 'MaxChargeVoltage'
let k10 = 'MaxCellVoltage'
let k11 = 'MinCellVoltage'
```

### Defaults

All default values can be changed from within the node-red ui. 


