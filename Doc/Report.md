# Resources

* For C-based dev platforms: https://github.com/linux-can/can-utils

* For Arduino based Platforms: https://copperhilltech.com/ard1939-sae-j1939-protocol-stack-for-aduino/

# Flowchart

<div style="width: 640px; height: 480px; margin: 10px; position: relative;"><iframe allowfullscreen frameborder="0" style="width:640px; height:480px" src="https://lucid.app/documents/embeddedchart/3cc1cbb4-475d-4121-a3e1-59e5741799bc" id="YnrNZDm0VoFh"></iframe></div>

The system goes into three different states and two critical functions. It is in *initial* state, moves into *operational* state after succesfully claiming the address and into *defunct* when no claimable addresses are left. While in initial or operational states, and upon reciecinng a contending address claim, it checks for a new address by scanning through the addresses in an increasing order from the current one. If an address is found, it moves back into the initial state, sends a claim, waits for contention and moves into operational after claiming the address. Otherwise, it moves into defunct where it only responds to requests using the intial or 0xFE address. It stays in defunct untill terminated.

# Interface Setup

* *iface* can be vcan0 (type vcan) or can0, can1 etc. (type: can)

* Check if interface is already setup

  ```bash
  ifconfig| grep <iface>
  ```

* If type is vcan, 

  ```bash
  sudo modprobe vcan
  ```

* Load the interface

  ```bash
  sudo ip link add <iface> type <type>
  ```

* Set it up

  ```bash
  sudo ip link set up <iface>
  ```

* Check if it is ready

  ```bash
  ifconfig <iface>
  ```

  Should return something.