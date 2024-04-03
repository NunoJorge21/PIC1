---
title: "Week 6"
date: 2024-03-29T22:00:00+06:00
image_webp: images/blog/circuito_W6.webp
image: images/blog/circuito_W6.jpg
author: SSM Team
description: "This is meta description"
---

In the 3rd meeting with our project assistant, we confirmed the necessary features for the intermediate delivery, namely the acquisition of pure sinusoids and its representation in both time and frequency domains.

We also discussed with our partners at XLR the possibility of integrating our system with the d&b ArrayCalc software. We decided to get in touch with other companies first, since d&b tends to be less open to external proposals.

> Some of the other companies to consider are the developers of the RiTA software and the NEXT Audiogroup.  

We displayed our first spectres and time domain readings. We have yet to calibrate the microphone, so far we cannot read the power(decibels).
Our prototype is activated with a button push which triggers a reading(C++ code running in Arduino).
This reading is sent through a microUSB cable with serial communication to a computer running a python script.
The first version of this python script extracted the data to a .csv file to be used by a MATLAB script(for plotting and calculations).
The final version of the week plots acquires the data from the port and plots it without using MATLAB.

We also implemented a system to monitor our site's visits.


