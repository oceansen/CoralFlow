import sys
from bluepy import btle
from bluepy.btle import UUID, Peripheral
import binascii
import time
import numpy as np
import struct
import tflite_runtime.interpreter as tflite
import numpy as np
import pandas as pd
import threading

#Flow sensor address, service, and characteristic
flow_ble_address = "f3:aa:b3:f6:ab:b0"

flow_ble_service_uuid = UUID('ffb0')
flow_ble_characteristic_uuid = UUID('ffb3')


#Prediction Parameters
breathing_min=0
breathing_max=4096
breathing_range = breathing_max - breathing_min
slope_shift=2
lookBackInRealtime = 50 # Number of points to lookback, must be less than 100, higher the number more current the value but with more variability

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
        self.buffer=[]
        self.abdomen=[]
        self.abdomen_slope_sin=None
        self.abdomen_slope_cos=None
        self.inputToNN = None
        self.currentPower=[]
        self.interpreter = tflite.Interpreter(model_path="/home/pi/Sagar/CoralFlow/models/model.tflite")
        self.interpreter.allocate_tensors()
        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        # ... initialise here

    def handleNotification(self, cHandle, data):
        #Unpack integer values for breathing data
        tuples = struct.unpack('hhhhhhhl',data)
        self.buffer.extend(list(tuples)[:-1])
        
        #Run the loop to process a buffer of 100 sensor values 
        if(len(self.buffer)>100):
            self.abdomen=self.buffer[-100:]
            self.buffer = self.buffer[-lookBackInRealtime:]   
            self.featurize()
            self.predict()
        if(len(self.currentPower)>1):
            self.printPower()
            
            
    def featurize(self):
        data=pd.DataFrame(self.abdomen)
        #Normalize
        data= (data - breathing_min)/breathing_range
        slope=calculate_slope(data, slope_shift,rolling_mean_window=1, absvalue=False)
        self.abdomen_slope_sin=np.sin(slope)       
        self.abdomen_slope_cos=np.cos(slope)
        self.inputToNN = np.hstack(( self.abdomen_slope_sin,  self.abdomen_slope_cos))
        self.inputToNN = np.array(self.inputToNN).reshape(1, 100, 2)
  
    def predict(self):
        # Test the model on random input data.
        #input_shape = input_details[0]['shape']
        #input_data_random = np.array(np.random.random_sample(input_shape), dtype=np.float32)

        input_data=np.array(self.inputToNN,dtype=np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        self.currentPower.extend(output_data)
        if(len(self.currentPower)==100):
            self.currentPower=self.currentPower[-1]
        
    def printPower(self):
        #threading.Timer(5.0, self.printPower).start()
        #print("Input="+str(self.abdomen))
        
        print("Estimated Power="+str(self.currentPower[-1])+"Watts")

def calculate_slope(data, shift=2, rolling_mean_window=1, absvalue=False):
    """Calculate slope.

    Args:
        data (array): Data for slope calculation.
        shift (int): How many steps backwards to go when calculating the slope.
            For example: If shift=2, the slope is calculated from the data
            point two time steps ago to the data point at the current time
            step.
        rolling_mean_window (int): Window for calculating rolling mean.

    Returns:
        slope (array): Array of slope angle.

    """

    v_dist = data - data.shift(shift,fill_value=0)
    h_dist = 0.1 * shift

    slope = np.arctan(v_dist / h_dist)

    if absvalue:
        slope = np.abs(slope)

    slope = slope.rolling(rolling_mean_window).mean()

    return slope



if __name__ == "__main__":
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
