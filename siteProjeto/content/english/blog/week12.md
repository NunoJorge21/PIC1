---
Title: "Week 12"
date: 2024-05-10T22:00:00+06:00
image_webp: images/blog/interviews.webp
image: images/blog/interviews.jpg
author: SSM Team
description: "This is meta description"
---

This week has been dedicated to the study and implementation of the communications protocol. The primary objective is to establish a reliable data transmission from the Arduino Nano RP2040 to a gateway, facilitated by a WEMOS D1 mini directly connected to the computer. Given our shift in focus towards outdoor applications, it is imperative that the chosen communication method supports long-distance transmission. Consequently, the LoRa protocol has been deemed the most suitable option.

However, it became apparent that the low bit rate offered by the LoRa modules when connected to an Arduino would result in extended transmission times for large volumes of data. Initially, our aim was to transmit raw audio data directly via LoRa. However, tests indicated that this method would require approximately twenty seconds for completion. In light of this, alternative solutions were explored to address this challenge:

 - Compression of the sampled audio file using an MP3-like algorithm.
 - Implementation of delta encoding to reduce the required data volume.
 - Transmission of the Fourier Transform data, representing half the size of the raw audio file.

The first option proved unfeasible due to the computational demands of MP3 algorithms, which exceed the capabilities of the Arduino's processing power. However, since the receiver is connected to a computer, decompression overhead is not a concern. While delta encoding appeared initially promising, the variable nature of audio files renders its efficacy minimal. Ultimately, the third option was deemed the most viable.

Initially, we considered developing a custom complex number library for the necessary calculations. However, recognizing the quadratic complexity (O(n^2)) of this approach, we opted for the EasyFFT algorithm, which boasts a more favorable complexity of O(n*log(n)). Consequently, the total processing time was reduced to approximately 10 seconds, encompassing both calculation and data transmission/reception.

Ensuring precise representation of transmitted data requires calibration of the Arduino microphone to attain coherent audio values. Furthermore, significant strides have been taken in integrating the GPS module, notwithstanding an unforeseen setback during testing resulting in its malfunction. Nonetheless, with an additional module on hand, we are poised to restore full functionality and to test the communications along with the GUI by the end of next week. These objectives mark our next milestones for the project.