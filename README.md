# AMP-Challenge-04-BBB-Address-Claim
 
This challenge uses the BeagleBone Black with a Truck Cape. There will be a C-based program that claims an address from J1939. This program is an extension of the previous challenge, the patched brake-light-flasher code. In addition to previous stimulation scripts, there is a python script `address_attack.py` that will be used to run as the malicious actor performing an address claim attack.

## Quick Start

 There are two ways to get this repo onto the BeagleBone Black. Either plug the USB cable into your PC, and run 
```
cd <this_repo_location>
./reload.sh
```
Or ssh into the BBB and do the below steps:

- `ssh debian@192.168.7.2` # (or your BBB IP if modified) The default password is temppwd

- Generate personal access token
  - https://github.com/settings/tokens
  - Save token to use for logging in
- Clone the repo directly onto the BBB

```
cd /home/debian && git clone https://github.com/SystemsCyber/AMP-Challenge-04-BBB-Address-Claim.git
cd AMP-Challenge-04-BBB-Address-Claim
```

- Run the program
```
./build/program_c.gcc.vuln vcan0
```

- In another terminal you can use this to view the CAN traffic
```
candump vcan0
```

- (Optional) Verify LED indicators are working as from Challenge 03

- Launch the attacking node from yet another terminal
```
cd AMP-Challenge-04-BBB-Address-Claim
python3 address_attack.py vcan0
```

- The observed behavior should show the CAN addresses are exhausted in the terminal running the vulnerable binary. Additionally, the CAN traffic will stop. 

- You can terminate any of the running programs with `Ctrl-C`.


## Introduction

In J1939/81, dynamic address allocation is possible. This allows nodes to be dynamically added to the network, and is useful for expanding pre-established systems. Under this protocol, it is possible to claim an existing node's address if the requesting node has higher priority. A malicious actor can abuse this protocol feature to request all addresses on the network, with the highest priority, leading to a denial of service. The provided challenge will demonstrate the situation, and give insight into the industry and how it may mitigate such a situation.

The provided program './build/program_c<version>' runs as a node on a J1939 network. It starts off with a default (dynamic) network address. Once the malicious actor is running, it will attempt to kick the running client off of the network by claiming its current address. The attacking program will then proceed to the next address. This process will continue until the provided client has no addresses left to use except for that of the *idle* address, which is 254 (0xfe).

Challenge 04 additionally introduces a reporting feature into the brake light controller. This will indicate the light status of the bumper over the network. This reporting feature changes its source address to the current dynamic address, and if all addresses are exhausted, the reporting will cease.

You can use the following flowchart to get an idea of how this program will make its decisions based on the J1939 traffic.

[Address Claim Flowchart](Doc/Address_Claim_Procedure_Flow_Diagram.pdf)

## The Vulnerability

The vulnerability can be seen as the defunct state when all addresses are exhausted due to a malicious actor. The brake-light-flasher will lose the ability to send status reports over the network if all dynamic addresses are claimed. This can be seen when the binary enters the idle or defunct state, which will no longer attempt to report over the network.

## The Fix

There are several fixes to this issues:

**Ignore the final address claim:**
This is a trivial patch, but it deviates from the J1939 specification. In this patch, the brake-light-flasher will never bind to the idle address and thus keep its last known dynamic address.

**Switch to static:**
After exhausting the dynamic range, the binary will revert to a static address outside the range of dynamically allocated addresses. This patch will come with two candidates, one changing the structure of the patched function, and another adding minimal changes to the function.

## Software

The software for this program is all located in the *program_c/* directory which includes an extension of the previous challenge's C source code. This extension is the address claim functionality and status reporting. The compiled binaries can be found at in the *./build/* directory.

Source code for the challenge follows the previous challenge's layout. Source .c files can be found under `./program_c/src/*.c` and the patch can be found at `./program_c/src/main.patch`. As with the previous challenge, the patch will be applied accordingly based on the make commands used to build, if re-compilation is desired. For a simple case, in order to build everything, just type `make` in this directory.

In order to run the challenge binary, it must first be placed onto the BeagleBone Black. This can e
asily be accomplished by running `./reload.sh`, which will look for an environment variable `BBB` which is set with the BeagleBone Black's IP address, and additionally check for default addresses. This is followed by syncing the current directory with the equivalent on the embedded device at /home/debian/\<name-of-this-repository\>. Additionally, an IP address can be provided as an argument to the script `./reload.sh <IP-Addr-of-BBB>` if it was changed.

Next, run the binary `./build/program_c<version> [can0/vcan0]`. This will setup connections on the CAN interface, which is stimulated by the provided stimulation scripts.

Once the challenge program is running, ./address_attack.py can be launched by `python3 address_attack.py [can_interface]` to mimic the attacker and kick the program (program_c) offline if it is not patched. This can either be done via another terminal (and thus possibly ssh connection), or sending the previous program into the backgound with something like `<Ctrl+z> ; bg ; python3 address_attack.py [can_interface]`.

Inside of the *./build/* directory, you will encounter a list of binaries. They should be self explanatory. The name of the binary follows this convention: `program_<language>.<compiler>.<vuln|type_of_patch>`.

### Testing

In addition to the provided challenge and attacker script, a bit of relevant unit testing has been provided for the interested parties. Currently, there are several functions from main.c which are tested. In the current implementation, two of these tests will fail if the binary is not patched. Other tests are there to support the confirmation of correct operation upon patching.

The testing framework invocation as well as test cases can be found in *./program_c/src/testing/*. In order to run the tests, you can simply change into that directory and type `make`. If anything needs to be compiled it will be, followed by a run of the created test binary *tests*.

Additionally, one can see one of the patched binaries pass all of the tests by running
```Makefile
make clean
make -e PATCH=<patch_type> testspatched
```
The PATCH environment variable should match the file extensions from `program_c/src/main.c.<patch_type>`. This will create a patched version of main.c and place it in /tmp/main.c to be used to compile a new test framework.

## Hardware

There is no new hardware for this challenge. Everything will run on the previously provided Heavy Truck Cape with BeagleBone black.

## Challenge Setup

The physical connections here are the same as those from Challenge 03.

## Build Chain

The current challenge is built on a Linux platform. It has been tested using Ubuntu 18.04 for desktop and additionally running on the BeagleBone Black on top of the "Debian GNU/Linux 10 (buster)" OS. The team has leveraged GNU Make in order to save recompilation time for certain scenarios. There are rules within the Makefiles to compile different binaries depending upon the arguments fed to Make. All of the vulnerable and patched binary programs can be found in the top level *build/* directory after the compilation, assembly and linking processes have been completed.

Without an understanding of GNU Make, you can run `make` from this current directory. Without any arguments, it will build the corresponding challenge programs and put them in the *build/* directory. The testing environment can be easily launched in the same manner (by running `make` with no arguments) from within the *program_c/src/testing/* directory. 

The compilers used (Gcc and Clang) are the default installed binaries which have been supplied in the OS image, or have been installed to the default locations by leveraging the `apt` command line package management system. Further details about the commands used for creating the binaries can be extrapolated by looking at the Makefiles (which includes makefile or Makefile) anywhere in this repository's tree.

## Relevant Specifications

[Address Claim Flowchart](Doc/Address_Claim_Procedure_Flow_Diagram.pdf)

### Bumper Status Reporting

While the binary is in an operational state, it will report LED state. There are two states represented, on and off, and are 0xFF and 0x00 respectively. The outer left, inner left, inner right, and outer right are in sequential order at byte 2, 4, 6, and 8 (1 indexed). The extended Arbitration ID will be 0x1CFE4000 logically OR'd with the current source address, so a source address of 127 would result in an extended arbitration ID of 0x1CFE407F.  

