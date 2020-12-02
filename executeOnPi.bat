
::Copy TensorFlow Lite Model and Compile Edge TPU version
scp models/model.tflite pi@raspberrypi.local:/home/pi/Sagar/CoralFlow/models

::Command to install required libraries on Raspberry Pi
::ssh pi@raspberrypi.local "pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp35-cp35m-linux_armv7l.whl"
::ssh pi@raspberrypi.local "pip3 install scikit-learn --index-url https://piwheels.org/simple"

::Execute CoralFlow to Connect to Bluetooth Sensor and use Model on Sensor Data
scp coralflow.py pi@raspberrypi.local:/home/pi/Sagar/CoralFlow

ssh pi@raspberrypi.local "python3 /home/pi/Sagar/CoralFlow/coralflow.py"
