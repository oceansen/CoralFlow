import sys
from bluepy import btle
from bluepy.btle import UUID, Peripheral
import binascii
import time
import numpy as np
import struct

#Flow sensor address, service, and characteristic
flow_ble_address = "f3:aa:b3:f6:ab:b0"
flow_ble_service_uuid = UUID('ffb0')
flow_ble_characteristic_uuid = UUID('ffb3')


# BLE heart rate service
#hr_ble_service_uuid ="0000180d-0000-1000-8000-00805f9b34fb"
# Heart rate measurement that notifies.
#hr_ble_characteristic_uuid= "00002a37-0000-1000-8000-00805f9b34fb";

def enable_notify(peripheral, service_uuid, char_uuid):
    setup_data = b"\x01\x00"
    svc = peripheral.getServiceByUUID(service_uuid)
    print(svc)
    ch = peripheral.getCharacteristics(uuid=char_uuid)[0]
    print(ch)
    print('Characteristic handle: %d' % ch.valHandle)
    notify_handle = ch.getHandle() + 1
    peripheral.writeCharacteristic(notify_handle, setup_data, withResponse=True)

class FlowDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        print(data)
        #Unpack integer values for breathing data
        tuples = struct.unpack('hhhhhhhl',data)
        print(tuples)

        


# attempt connecting
try:
    print('Connecting to ' + flow_ble_address)
    _ble_peripheral = btle.Peripheral(flow_ble_address, addrType=btle.ADDR_TYPE_RANDOM)
    _ble_peripheral.withDelegate(FlowDelegate())
    # Setup to turn notifications on, e.g.
    enable_notify(_ble_peripheral, flow_ble_service_uuid, flow_ble_characteristic_uuid )
except Exception as e:
    print(e)
# Main loop ——–
while True:
    if _ble_peripheral.waitForNotifications(0.007):
    # handleNotification() was called in delegate
        continue
 # inform user main loop is running
    sys.stdout.write('.')
    sys.stdout.flush()
