### **EIGHT** **HARDWARE**


When you are writing code, you may need to know how each module works or the role of each pin, then please see this
chapter.


In this chapter you will find a description of each module’s function, technical parameters and working principle.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **8.1 Robot HAT**


is a multifunctional expansion board that allows Raspberry Pi to be quickly turned into a robot. An MCU is on board
to extend the PWM output and ADC input for the Raspberry Pi, as well as a motor driver chip, I2S audio module and
mono speaker. As well as the GPIOs that lead out of the Raspberry Pi itself.


It also comes with a Speaker, which can be used to play background music, sound effects and implement TTS functions
to make your project more interesting.


Accepts 7-12V power input with 2 battery indicators, 1 charge indicator and 1 power indicator. The board also has a
user available LED and a button for you to quickly test some effects.


For detailed instructions, please refer to: .


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


**243**


**SunFounder PiCar-X Kit**


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **8.2 Camera Module**


**Description**


This is a 5MP Raspberry Pi camera module with OV5647 sensor. It’s plug and play, connect the included ribbon cable
to the CSI (Camera Serial Interface) port on your Raspberry Pi and you’re ready to go.


The board is small, about 25mm x 23mm x 9mm, and weighs 3g, making it ideal for mobile or other size and weightcritical applications. The camera module has a native resolution of 5 megapixels and has an on-board fixed focus lens
that captures still images at 2592 x 1944 pixels, and also supports 1080p30, 720p60 and 640x480p90 video.


**Note:** The module is only capable of capturing pictures and videos, not sound.


**Specification**


   - **Static Images Resolution** : 2592×1944


   - **Supported Video Resolution** : 1080p/30 fps, 720p/ 60fps and 640 x480p 60/90 video recording


   - **Aperture (F)** : 1.8


   - **Visual Angle** : 65 degree


   - **Dimension** : 24mmx23.5mmx8mm


   - **Weight** : 3g


   - **Interface** : CSI connector


   - **Supported OS** : Raspberry Pi OS(latest version recommended)


**Assemble the Camera Module**


On the camera module or Raspberry Pi, you will find a flat plastic connector. Carefully pull out the black fixing switch
until the fixing switch is partially pulled out. Insert the FFC cable into the plastic connector in the direction shown and
push the fixing switch back into place.


**244** **Chapter 8. Hardware**


**SunFounder PiCar-X Kit**


If the FFC wire is installed correctly, it will be straight and will not pull out when you gently pull on it. If not, reinstall
it again.


**Warning:** Do not install the camera with the power on, it may damage your camera.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**8.2. Camera Module** **245**


**SunFounder PiCar-X Kit**

### **8.3 Ultrasonic Module**


   - **TRIG** : Trigger Pulse Input


   - **ECHO** : Echo Pulse Output


   - **GND** : Ground


   - **VCC** : 5V Supply


This is the HC-SR04 ultrasonic distance sensor, providing non-contact measurement from 2 cm to 400 cm with a range
accuracy of up to 3 mm. Included on the module is an ultrasonic transmitter, a receiver and a control circuit.


You only need to connect 4 pins: VCC (power), Trig (trigger), Echo (receive) and GND (ground) to make it easy to use
for your measurement projects.


**Features**


  - Working Voltage: DC5V


  - Working Current: 16mA


  - Working Frequency: 40Hz


  - Max Range: 500cm


  - Min Range: 2cm


  - Trigger Input Signal: 10uS TTL pulse


  - Echo Output Signal: Input TTL lever signal and the range in proportion


  - Connector: XH2.54-4P


  - Dimension: 46x20.5x15 mm


**Principle**


The basic principles are as follows:


  - Using IO trigger for at least 10us high level signal.


  - The module sends an 8 cycle burst of ultrasound at 40 kHz and detects whether a pulse signal is received.


**246** **Chapter 8. Hardware**


**SunFounder PiCar-X Kit**


  - Echo will output a high level if a signal is returned; the duration of the high level is the time from emission to
return.


  - Distance = (high level time x velocity of sound (340M/S)) / 2


Formula:


  - us / 58 = centimeters distance


  - us / 148 = inch distance


  - distance = high level time x velocity (340M/S) / 2


**Application Notes**


  - This module should not be connected under power up, if necessary, let the module’s GND be connected first.
Otherwise, it will affect the work of the module.


  - The area of the object to be measured should be at least 0.5 square meters and as flat as possible. Otherwise, it
will affect results.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**8.3. Ultrasonic Module** **247**


**SunFounder PiCar-X Kit**

### **8.4 3-pin Battery**


   - **VCC** : Battery positive terminal, here there are two sets of VCC and GND is to increase the current and reduce
the resistance.


   - **Middle** : To balance the voltage between the two cells and thus protect the battery.


   - **GND** : Negative battery terminal.


This is a custom battery pack made by SunFounder consisting of two 18650 batteries with a capacity of 2000mAh. The
connector is XH2.54 3P, which can be charged directly after being inserted into the Robot HAT.


**Features**


  - Composition: Li-ion


  - Battery Capacity: 2000mAh, 14.8Wh


  - Battery Weight: 90.8g


  - Number of Cells: 2


**248** **Chapter 8. Hardware**


**SunFounder PiCar-X Kit**


  - Connector: XH2.54 3P


  - Over-discharge protection: 6.0V


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**8.4. 3-pin Battery** **249**


**SunFounder PiCar-X Kit**


**250** **Chapter 8. Hardware**


**CHAPTER**
