These are log files to stimulate the brake light controller without the use of the
provided GUI. Below is a short description of each file

### brake.log
This is a small 4 second log file used to quickly demonstrate a ehicle applying
brakes.

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | Brakes on, no speed, No signals |
| 3 | Previous state |
| 4 | Brakes off, no speed, No signals |

### everything.log
This demonstrates a wide variety of common behaviour. It **does not** demonstrate every
possible state/scenario a vehicle can be in. It is merely provided to quickly see
different vehicle behaviour 

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | brake on, no speed, No signals |
| 3 | Brakes off, no speed, No signals |
| 4 | Brakes off, no speed, left signal |
| 5 | Brakes off, no speed, hazard signal |
| 6 | Brakes off, no speed, right signal |
| 7 | Brakes off, no speed, No signals |
| 8 | brake on, Speed below threshold, No signals |
| 9 | Previous state |
| 10 | Brakes off, no speed, No signals |
| 11 | brake on, Speed above threshold, No signals  |
| 12 | Previous state |
| 13 | Brakes off, no speed, No signals |
| 14 | Brakes off, no speed, hazard signal |
| 15 | brake on, Speed below threshold, hazard signal|
| 16 | Brakes off, no speed, No signals |

### moving_over.log
The vehicle is starts to move, then applies brakes while still moving, over the
vulnerability threshold

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | Speed above threshold, brakes off, No signals |
| 3 | Speed above threshold, brakes on, No signals |
| 4 | previous state |
| 5 | previous state |
| 6 | Brakes off, no speed, No signals |

### moving_under.log
The vehicle is starts to move, then applies brakes while still moving, under the
vulnerability threshold

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | Speed under threshold, brakes off, No signals |
| 3 | Speed under threshold, brakes on, No signals |
| 4 | previous state |
| 5 | previous state |
| 6 | Brakes off, no speed, No signals |

### turn_moving_over.log
This log demonstrates a vehicle already moving, applying their turn signal, and then
braking above the vulnerability threshold

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | Speed above threshold, brakes off, Left signal |
| 3 | Speed above threshold, brakes on, Left signal |
| 4 | previous state |
| 5 | previous state |
| 6 | Brakes off, no speed, No signals |

### vuln.log
This is a small 4 second log that will quickly run the device through the vulnerable
behaviour

| Seconds (1 indexed) | Description |
| ------------------- | ----------- |
| 1 | Brakes off, no speed, No signals |
| 2 | Speed over threshold, Brakes on, No signals |
| 3 | Previous state |
| 4 | Brakes off, No signals |
