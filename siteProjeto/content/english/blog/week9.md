---
Title: "Week 9"
date: 2024-04-19T22:00:00+06:00
image_webp: images/blog/week9.webp
image: images/blog/week9.jpg
author: SSM Team
description: "This is meta description"
---

This week, we have made some necessary preparations to start working with the BLE beacons.

After reading Rita Abreu Martinho's Master's thesis on IIoT for Lean Production Systems, where she also used BLE beacons for the localization, and revisiting, now with a deeper understanding of the subject, documentation regarding these devices and the Arduino Nano RP2040 microcontroller board, we were able to outline various aspects worth taking into account while developing the prototype:
* Since we intend to come up with a solution that can easily be adapted to any venue, we shall not rely on equipment inherent to the room itself, such as Wi-Fi connection (as discussed in previous blog entries) and power sockets;
* Since we are going to use LoRa to send information from the Arduino to the gateway, special care must be taken to account for the very limited maximum packet size that this communication method allows; 
* Since we want to locate the Arduino board in the venue with considerable precision, the placement of the beacons must be strategically planned; 
* Minimizing the costs of our solution is of extreme importance.


Rita Martinho developed her thesis work in a warehouse; her goal was to determine the amount of time the workes of that warehouse would spend in each room. The solution she came up with relied on the power sockets that were available in each room: every room had a BLE receiver that was uninterruptedly scanning for BLE signals emitted by the beacons, that the workers carried in their pockets; she dealt with the energy consumption issue by plugging the receivers to the power sockets.

Because of the nature of our problem, this is not feasible. 
On the one hand, the BLE receivers have to be powered by batteries, requiring a smart consumption management (for instance, we can make it so that the user controls when the device is active). Still, we estimate the energy consumption to be relatively high, with the batteries only lasting around 1 week if heavily used.
On the other hand, it would be better for us to distribute beacons throughout the venue and attatch a receiver to the Arduino (and not the other way around). This can drastically reduce the costs of our product in two ways: the BLE beacons are generally much cheaper than just the Arduino Nano RP2040; even if we need to change the batteries of the receivers before each event, there are not that many of them and it is very easy to change their batteries (since they are not mounted in a fixed place somewhere in the venue). 

Regarding the actual localization of the microphone in the room, here is a brief descruption of the method we are currently considering to find its coordinates:
1. we start by defining a (2D) coordinate system vor the venue;
2. we then distribute the BLE beacons, making sure to know their precise location;
3. once the Arduino board with the microphone and BLE receiver is activated, it starts sampling the acoustic signal and scanning the BLE signals emitted by the beacons;
4. the Arduino sends, via LoRa, the sound samples and the information necessary to be able to locate it inside the venue to the gateway that is connected to the sound technicians' PC;
5. the program that is responsible for the Graphical User Interface receives these data, processes it and presents the results to the user.

The GUI we are planning to design consists of a 2D of the venue where we can access the points (identified in the map) where sound samples have been taken (i.e., locations of the room where our device has been activated).

There are still some considerations regarding the localization worth mentioning. The method we are currently considering to achieve this is the following: we know the precise location of each beacon; we estimate, at a given point in the venue, the distance from the receiver to each beacon; if we imagine a circunference centered in each beacon with the radius equal to the distance between that beacon and the receiver, we can see that the location of the receiver corresponds to the intersection of all those circunferences. We must not forget, however, that our equipment is not ideal; in particular, we might have to account for the fact that the range of the beacons is limited and the estimated distance to each beacon is not 100% accurate. 

Besides, we still need to decide if we estimate the Arduino's location in its code or along with the signal processing, in the code responsible for the GUI. The fisrt option allows us to send directly the location via LoRa, taking up little space in the pckets sent, but it would require a lot more computation in the Arduino itself, which would increase a lot its battery consumption. Even though the second option deals with this issue, it would make our solution largely dependent on the communications protocol (if, for instance, we need to change the number of BLE beacons used, the communications protocol would have to be adapted accordingly).

> Rita Martinho's Master's thesis: https://fenix.tecnico.ulisboa.pt/downloadFile/563345090419757/thesis_final_light_nov.pdf