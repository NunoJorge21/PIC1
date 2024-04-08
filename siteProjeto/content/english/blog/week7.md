---
Title: "Week 7"
date: 2024-04-05T22:00:00+06:00
image_webp: images/blog/interviews.webp
image: images/blog/interviews.jpg
author: SSM Team
description: "This is meta description"
---

On April 3rd, we had a meeting with our coordinator Luís Caldas de Oliveira and our assistant Rafael Cordeiro to discuss our first pitch deck.
Several shortcomigs were identified, including:
* esthetic issues;
* lack of presentation of results;
* lack of schematics of our current and future solutions
* lack of description current and future challenges

A further discussion was had regarding localization technologies.
Mentioned technologies:
* GPS -> more adequate in outdoor solutions;
* BLE Beacons -> cheap, but require multiple devices and previous placement;
* Ultra Wide Band -> allows for less devices, but very expensive;
* Extende Kalman Filters -> relevant for tracking moving targets;
* Wi-Fi -> very low accuracy.

At the moment, we the believe the most feasible option is to connect a gateway to a PC (where the Graphical User Interface is being executed) that communicates with the microcontrollers via LoRa. This is a relatively cheap solution that, besides being good enough for the distances and accuracy we are working with, does not require a server that we need do build and maintain. Regarding the localization, we are more likely to use BLE beacons since they are not expensive, they work indoors (if special care is taken in order to avoid interferences) and our professors already have some, so there is no need to order more equipment.

We also gave up on the idea of trying to couple system to already existent softwares; that is a possibility for future iterations of the project. We prefer to create our own GUI, even if it is rather simple, to avoid relying on external entities - which could pose significant challenges given the short time remaining until the final delivery.
