---
Title: "Week 9"
date: 2024-04-19T22:00:00+06:00
image_webp: images/blog/interviews.webp
image: images/blog/interviews.jpg
author: SSM Team
description: "This is meta description"
---

This week, we have made some necessary preparations to start working with the BLE beacons.
After reading Rita Abreu Martinho's Master's thesis on IIoT for Lean Production Systems - where she also used BLE beacons for the localization - and revisiting, now with a deeper understanding of the subject, documentation regarding these devices and the Arduino Nano RP2040 microcontroller board, we were able to outline various aspects worth taking into account while developing the prototype:
* Since we intend to come up with a solution that can easily be adapted to any venue, we shall not rely on equipment inherent to the room itself, such as Wi-Fi connection (as discussed in previous blog entries) and power sockets;
* Since we are going to use LoRa to send information from the Arduino to the gateway, special care must be taken to account for the very limited maximum packet size that this communication method allows; 
* Since we want to locate the Arduino board in the venue with considerable precision, the placement of the beacons must be strategically planned; 
* Minimizing the costs of our solution is of extreme importance.
