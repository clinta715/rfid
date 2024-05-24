Initial release of RFID program
Contains Python back-end that runs locally in a command prompt: this component communicates via serial port driver/usb serial port driver to the actual RFID reader itself.  It's my first Python application of any real significance is as you can tell is largely procedural and does not incorporate many OOP elements.  Also, a lot of the ideas and methods are things I would have used in DOS C/C++ code, array manipulation, etc.
However, it more or less works.  

The backend was done with Arduino, I modified an existing RFID reader codebase so that it would communicate with my RFID reading program using a very elementary 'protocol' (almost too simple to be called a protocol), via a local-loopback listening port.  It's written in C++ code, so in this exercise I have used C++, JavaScript, and Python.

Then the Chrome extension itself is written in JavaScript which I want to stress, when I wrote this program, I did not know any JavaScript since the days of Internet Explorer and the language has changed quite a bit since then.  There is a lot of poorly-structured Promise-based code too because I didn't want to stop my project and learn JavaScript.  I also had to learn quite a bit about CORS for this project.
