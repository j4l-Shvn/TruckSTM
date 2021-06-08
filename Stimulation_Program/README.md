This directory contains software to interface with the DPA 5 and stimulate the Brake Controler.
There are two python scripts that can be ran to accomplish this.

The **BrakeAndSpeedSignalGenerator.py** script will run a GUI application for sending brake and turn
singal messages, based on the state of the GUI. (ex; Is the brake button pressed? If so change CAN
traffic to reflect this)
- Run using `python .\BrakeAndSpeedSignalGenerator.py`
- Within the windows environment, the **BrakeAndSpeedSignalGenerator.py** file should also able to launch
by left clicking twice.

The second script, **sendlog.py** is used to send predefined log files, found in the **logs** directory.
The **logs** directory also contains a readme detailing what each log does, though the filenames also
reflect what the log should do.
- Run using `python .\sendlog.py .\logs\[filename]`
- Run the logs on repeat using `python -r .\sendlog.py .\logs\[filename]`
