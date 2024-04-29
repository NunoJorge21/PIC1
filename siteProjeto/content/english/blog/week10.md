---
Title: "Week 10"
date: 2024-04-26T22:00:00+06:00
image_webp: images/blog/interviews.webp
image: images/blog/interviews.jpg
author: SSM Team
description: "This is meta description"
---

In this week, as suggested by Prof. Luís Caldas, we began by discussing the spatial localization of the prototype using BLE Beacons with the responsible individuals at IStartLab. During this discussion, two main points were raised:

1º - The estimation of the object's position is achieved through fingerprinting of the sound intensities emitted by each Beacon, resulting in poor accuracy. The precision of this method is approximately 5 meters.
2º - BLE Beacon signals will be fixed at a specific height from the ground to simplify the problem. Consequently, the prototype will also need to be positioned at the same height to minimize errors. This necessitates the use of additional materials for the prototype.


Since the prototype is designed to automate the process of reading the acoustic properties of a room, such inconveniences defeat its purpose. Primarily, our product focuses on retrieving information from a designated point where the Arduino is located and transmitting all data to the user interface, thus reducing the number of individuals involved and the complexity of the task. However, based on the points raised during the discussion at IStartLab, we have concluded that, in its current state, our solution does not effectively address the issues. The poor localization and assembly of the instrument defy the expected cost/quality ratio.

As a result, we have decided to shift our focus to the outdoor environment to leverage the accurate localization provided by GPS.

Progress has also been made on the interface. We are currently working on mapping the environment into squares, assigning a specific sound intensity in decibels (dB) to each one.