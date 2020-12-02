# CoralFlow
This program runs on the Raspberry Pi and computes power in watts (as measured on the Concept2 Power Bike) from abdominal breathing measured using the Sweetzpot Flow sensor: https://www.sweetzpot.com/.

The program uses a machine learning model primarily developed for predicting cycling power.


Simple steps to using the tool.


Step 1: 

Change the MAC address of the Flow Bluetooth Sensor in main.py


flow_ble_address = "f3:aa:b3:f6:ab:b0"



Step 2:

Connect a Raspberry Pi 4.0 to your Windows PC and make sure it is connected to mobile hotspot of the PC
Also ensure that the Pi can be connected to without password and SSH.

Default login: pi
Default password: raspberry

Run ./executeOnPi.bat

Step 3:

Wear the Sweetzpot Flow Sensor between the ribcage and abdomen and observe the estimated power output from the ML model on the terminal


Contact sagar.sen@sintef.no for help and support if you are interested in the concept.



