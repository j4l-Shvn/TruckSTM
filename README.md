# AMP-Challenge-05-CAN-Log-Encryption

## Introduction
Logging CAN traffic can be helpful to understand the performance of the system. However, typical CAN data is insecure. Logging strategies require buffers to gather many short messages with low latency and then writing larger data blocks to media, like an SD card. If the data is not encrypted it could be accessed, modified, or exfiltrated by malicious actors. Challenge 05 will implement a patch which uses an external library to add AES encryption to the buffer of CAN data before it is written to the SD Card. 
The target brake light controller will perform the same actions as in Challenge 03 and Challenge 04. Received CAN messages will illuminate lights and the data contents will be buffered and written to an output file within the file system. Message count, message timing, and the integrity of the message contents will be maintained for the encrypted alternative. 

## Challenge Hardware Kit
The Challenge 05 Kit will provide each performer team with the original (vulnerable) software compiled for the target ARM development board, the appropriate patch, and the suite of test inputs and code needed to exercise the software. All source code for the original executable and the patch will be provided. 
This material will be provided to performers as part of Challenge Event 02 which will align with the twelve-month PI meeting in July of 2021. This challenge will leverage the model bumper, BeagleBone Brake Light Controller, and truck simulation kit already provided to the performers. Software, documentation, and tutorial videos will be provided by the AIS team via the Github repository. This challenge will also provide performers with the relevant sections of SAE specifications that outline bus arbitration and prioritization, message timing, and message structures. 

Performers will have J1939 connected prototyping boards that were used in Challenge 03, including the simulated brake light setup. This kit includes a CAN transceiver and a connection to the DPA 5 Pro. J1939 messages received by the software application running on the BeagleBone Black based brake light controller will be logged to a output file for later review.  Software will be provided to simulate speed and brake pedal presses in the CAN message it produces. 

### Implementation and Evaluation
A requirement exists for logging devices to capture 100% CAN bus load and store for diagnostic and/or forensic purposes. In the event that the device is compromised by a malicious actor the integrity of the logged data can be questioned. The logging feature of the software will be modified to enable encryption of the data as it is logged to internal storage.


# Challenge 05b: PowerPC Log Data Encryption 
Challenge 05b will be designed to expose performers to the platforms that may be encountered in later phases of the effort. For the purposes of this challenge, team AIS will build a bus gateway/bridge based on an NXP automotive PowerPC microcontroller development kit. This device will be responsible for passing data between the J1939 bus and other networks. As with Challenge 05, all messages on the bus will be logged to an output file. The contents of this file will be unencrypted, and the patch will be responsible for implementing an encryption routine to maintain the integrity of the data in the event of a compromise. Network traffic for this scenario will be representative of what may be encountered when working on a vehicle bus to include multiple devices communicating and a high volume of data. 

The source code and patches will be in the PowerPC directory
## Challenge 05b Hardware Kit
The development board from NXP is the DEVKIT-MPC5748G. This dev board has a series of LEDs to emulate the brake light LEDs. There is a CAN bus available to read messages from the external network for logging. The DEVKIT also has an SD Card holder. The Challenge 05b Kit will provide each performer team with the original (vulnerable) software compiled for the target PPC development board, the appropriate patch, and the suite of test inputs and code needed to exercise the software. All source code for the original executable and the patch will be provided. 

This challenge will leverage the truck simulation kit already provided to the performers. Software, documentation, and tutorial videos will be provided by the AIS team via the Github repository. This challenge will also provide performers with the relevant sections of SAE specifications that outline bus arbitration and prioritization, message timing, and message structures. This material will be posted by AIS in July of 2021.

# Stimulation Program
Software will be provided to simulate a standard network traffic load. 

