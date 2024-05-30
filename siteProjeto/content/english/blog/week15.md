---
Title: "Week 15"
date: 2024-05-31T22:00:00+06:00
image_webp: images/blog/interviews.webp
image: images/blog/interviews.jpg
author: SSM Team
description: "This is meta description"
---

On tuesday, 25th of May, Carlos Reis and Gonçalo Lázaro proceeded with MEMS microphone calibration.

For the effect, Prof. Luís Caldas de Oliveira allowed access to the IST anechoic chamber ,a Brüel&Kjaer Precision Integrating Sound Level Meter type2230 and a pistonphone calibrated for 94dBSPL at 1kHz.
The pistonphone was used to fine tune the sound level meter by providing a calibrated sound source(know intensity and frequency).

In the anechoic chamber a series of measurements were taken of the sound pressure level(dBSPL) generated by a collumn speaker providing a 1kHz signal.
The prototype was placed close to the sound meter and the values provided by both instruments were registered.

the sound meter was kept in Fast Aquisition Mode to aproximate the speeds of the two instruments and its values were taken by hand. For the prototype, each reading consisted in an array of 512 samples from which the root mean squared was calculated and used for further calculations. These proceedings were done with a C++ sketch and by using serial comunication with PC for the data extraction.

A linear regression was used to find a relative gain and a reference level, this are, parameters that allow the conversion of the MEMS output(a 16-bit integer) to dBSPL with the same reference as the sound meter. As the readings from the MEMS were linear with SPL and from the sound meter were logarithmic, some extra manipulation was necessary before applying the linear regression. However, all approximations were kept as reasonable as possible:
-we assumed no signal from the MEMS at 0 Pascal(reasonable but not provided by literature)
-equal frequency gain around the 1kHz

In theory, the parameters found will depend only on the MEMS manufacturing processes and all microphones of the same model should respect the same values. This means that this calibration was achieved for all MP34DT06J microphones and not just the one used. The software we develop can then be copied to all eventual copies of the device with no need for recalibration.

This calibration was then tested against the sound meter with the source at 1kHZ again and errors were in the range of 1%, never exceeding 20% for very quiet ambients (generally not found outside an anechoic chamber and not relevant to outdoor applications).