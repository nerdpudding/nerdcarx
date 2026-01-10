### **FIVE** **PLAY WITH EZBLOCK**


For beginners and novices, EzBlock is a software development platform offered by SunFounder for Raspberry Pi.
Ezbock offers two programming environments: a graphical environment and a Python environment.


It is available for almost all types of devices, including Mac, PC, and Android.


Here is a tutorial to help you complete EzBlock installation, download, and use.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.1 Quick Guide on EzBlock**


The angle range of the servo is -90~90, but the angle set at the factory is random, maybe 0°, maybe 45°; if we assemble
it with such an angle directly, it will lead to a chaotic state after the robot runs the code, or worse, it will cause the servo
to block and burn out.


So here we need to set all the servo angles to 0° and then install them, so that the servo angle is in the middle, no matter
which direction to turn.


[1. Firstly, Install EzBlock OS (EzBlock’s own tutorials) onto a Micro SD card, once the installation is complete,](https://docs.sunfounder.com/projects/ezblock3/en/latest/quick_guide_3.2/install_ezblock_os.html#install-ezblock-os-latest)
insert it into the Raspberry Pi.


**Note:** After the installation is complete, please return to this page.


**159**


**SunFounder PiCar-X Kit**


2. To ensure that the servo has been properly set to 0°, first insert the servo arm into the servo shaft and then gently
rotate the rocker arm to a different angle. This servo arm is just to allow you to clearly see that the servo is
rotating.


3. Follow the instructions on the assembly foldout, insert the battery cable and turn the power switch to the ON.
Then plug in a powered USB-C cable to activate the battery. Wait for 1-2 minutes, there will be a sound to
indicate that the Raspberry Pi boots successfully.


**160** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


4. Next, plug the servo cable into the P11 port as follows.


5. Press and hold the **USR** key, then press the **RST** key to execute the servo zeroing script within the system. When
you see the servo arm rotate to a position(This is the 0° position, which is a random location and may not be
vertical or parallel.), it indicates that the program has run.


**5.1. Quick Guide on EzBlock** **161**


**SunFounder PiCar-X Kit**


**Note:** This step only needs to be done once; afterward, simply insert other servo wires, and they will
automatically zero.


6. Now, remove the servo arm, ensuring the servo wire remains connected, and do not turn off the power. Then
continue the assembly following the paper assembly instructions.


**Note:**


  - Do not unplug this servo cable before fastening this servo with the servo screw, you can unplug it after fastening.


  - Do not turn the servo while it is powered on to avoid damage; if the servo shaft is inserted at the wrong angle,
pull out the servo and reinsert it.


  - Before assembling each servo, you need to plug the servo cable into P11 and turn on the power to set its angle to
0°.


  - This zeroing function will be disabled if you download a program to the robot later with the EzBlock APP.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


**162** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.2 Install and Configure EzBlock Studio**


As soon as the robot is assembled, you will need to carry out some basic operations.


[• Install EzBlock Studio: Download and install EzBlock Studio on your device or use the web-based version.](https://docs.sunfounder.com/projects/ezblock3/en/latest/quick_guide_3.2/install_ezblock_app.html#install-ezblock-app-latest)


**Note:** If you are using the Raspberry Pi 5, please download the Beat version. Have any questions or issues during
using? please don’t hesitate to contact us.


[• Connect the Product and EzBlock: Configure Wi-Fi, Bluetooth and calibrate before use.](https://docs.sunfounder.com/projects/ezblock3/en/latest/quick_guide_3.2/connect_product_ezblock.html#connect-product-ezblock-latest)


[• Open and Run Examples: View or run the related example directly.](https://docs.sunfounder.com/projects/ezblock3/en/latest/quick_guide_3.2/open_run.html#open-run-latest)


**Note:** After you connect the Picar-x, there will be a calibration step. This is because of possible deviations in the
installation process or limitations of the servos themselves, making some servo angles slightly tilted, so you can calibrate
them in this step.


But if you think the assembly is perfect and no calibration is needed, you can also skip this step.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


**5.2. Install and Configure EzBlock Studio** **163**


**SunFounder PiCar-X Kit**


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.3 Calibrate the Car**


After you connect the PiCar-X, there will be a calibration step. This is because of possible deviations in the installation
process or limitations of the servos themselves, making some servo angles slightly tilted, so you can calibrate them in
this step.


But if you think the assembly is perfect and no calibration is needed, you can also skip this step.


**Note:** If you want to recalibrate the robot during use, please follow the steps below.


1. You can open the product detail page by clicking the connect icon in the upper left corner.


2. Click the **Settings** button.


**164** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


3. On this page, you can change the product name, product type, view the app version or calibrate the robot. Once
you click on **Calibrate** you can go to the calibration page.


The calibration steps are as follows:


**5.3. Calibrate the Car** **165**


**SunFounder PiCar-X Kit**


1. Once you get to the calibration page, there will be two prompt points telling you where to calibrate.


**Note:** Calibrating is a micro-adjustment process. It is recommended to take the part off and reassemble it if you click a button to the limit and the part is still off.


2. Click on the left prompt point to calibrate the PiCar-X’s Pan-Tilt(the camera part). By using the two sets of
buttons on the right, you can slowly adjust the Pan-Tilt’s orientation, as well as view their angles. When the
adjustment is complete, click on **Confirm** .


**166** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


3. To calibrate the front wheel orientation, click on the right prompt point. Use the two buttons on the right to get
the front wheel facing straight ahead. When the adjustment is done, click on **Confirm** .


**Projects**


**5.3. Calibrate the Car** **167**


**SunFounder PiCar-X Kit**


This section begins with basic programming functions for the PiCar-X, and continues through to creating more advanced programs in Ezblock Studio. Each tutorial contains TIPS that introduce new functions, allowing users to write
the corresponding program. There is also a complete reference code in the Example section that can be directly used.
We suggest attempting the programming without using the code in the Example sections, and enjoy the fun experience
of overcoming the challenges!


All of the Ezblock projects have been uploaded to Ezblock Studio’s Examples page. From the Examples page, users
can run the programs directly, or edit the examples and save them into the users My Projects folder.


The Examples page allows users to choose between Block or Python language. The projects in this section only explain
[Block language, for an explanation of the Python code, please review this file to help you understand the Python code.](https://github.com/sunfounder/picar-x/blob/v2.0/docs/(EN)%20picarmini.md)


**Basic**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.4 Move**


This first project teaches how to program movement actions for the PiCar-X. In this project, the program will tell the
PiCar-X to execute five actions in order: “forward”, “backward”, “turn left”, “turn right”, and “stop”.


To learn the basic usage of Ezblock Studio, please read through the following two sections:


[• How to Create a New Project?](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


**168** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**TIPS**


This block will make the PiCar-X move forward at a speed based on a percentage of available power. In the example
below “50” is 50% of power, or half-speed.


This block will make the PiCar-X move backward at a speed based on a percentage of available power.


This block adjusts the orientation of the front wheels. The range is “-45” to ”45”. In the example below, “-30” means
the wheels will turn 30° to the left.


**5.4. Move** **169**


**SunFounder PiCar-X Kit**


This block will cause a timed break between commands, based on milliseconds. In the example below, the PiCar-X
will wait for 1 second (1000 milliseconds) before executing the next command.


This block will bring the PiCar-X to a complete stop.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**170** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**5.4. Move** **171**


**SunFounder PiCar-X Kit**


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.5 Remote Control**


This project will teach how to remotely control the PiCar-X with the Joystick widget. Note: After dragging and dropping
the Joystick widget from the Remote Control page, use the “Map” function to calibrate the Joysticks X-axis and Y-axis
readings. For more information on the Remote Control function, please reference the following link:


[• How to Use the Remote Control Function?](https://docs.sunfounder.com/projects/ezblock3/en/latest/remote.html#remote-control-latest)


**TIPS**


To use the remote control function, open the Remote Control page from the left side of the main page.


**172** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


Drag a Joystick to the central area of the Remote Control page. Toggling the white point in the center, and gently
dragging in any direction will produce an (X,Y) coordinate. The range of the X-axis or Y-axis is defaulted to “-100”
to “100”. Toggling the white point and dragging it directly to the far left of the Joystick will result in an X value of
“-100” and a Y value of “0”.


After dragging and dropping a widget on the remote control page, a new category-Remote with the above block will
appear. This block reads the Joystick value in the Remote Control page. You can click the drop-down menu to switch
to the Y-axis reading.


The map value block can remap a number from one range to another. If the range is set to 0 to 100, and the map value
number is 50, then it is at a 50% position of the range, or “50”. If the range is set to 0 to 255 and the map value number
is 50, then it is at a 50% position of the range, or “127.5”.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.5. Remote Control** **173**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.6 Test Ultrasonic Module**


PiCar-X has a built-in Ultrasonic Sensor module that can be used for obstacle avoidance and automatic object-following
experiments. In this lesson the module will read a distance in centimeters (24 cm = 1 inch), and **Print** the results in a
**Debug** window.


**TIPS**


**174** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


The **Ultrasonic get distance** block will read the distance from the PiCar-X to an obstacle directly ahead.


This program is simplified with a **Variable** . For example, when there are multiple functions in a program that each
need to use the distance to an obstacle, a **Variable** can be used to report the same distance value to each function,
instead of each function reading the same value separately.


Click the **Create variable...** button on the **Variables** category, and use the drop-down arrow to select the variable
named “distance”.


The **Print** function can print data such as variables and text for easy debugging.


**5.6. Test Ultrasonic Module** **175**


**SunFounder PiCar-X Kit**


Once the code is running, enable the debug monitor by clicking the **Debug** icon in the bottom left corner.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


**176** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.7 Test Grayscale Module**


PiCar-X includes a Grayscale module for implementing line-following, cliff detection, and other fun experiments. The
Grayscale module has three detection sensors that will each report a value according to the shade of color detected by
the sensor. For example, a sensor reading the shade of pure black will return a value of “0”.


**TIPS**


Use the **Grayscale module** block to read the value of one of the sensors. In the example above, the “A0” sensor is the
sensor on the far left of the PiCar-X. Use the drop-down arrow to change the sensor to “A1” (center sensor), or “A2”
(far right sensor).


The program is simplified with a **create list with** block. A **List** is used in the same way as a single **Variable**, but in
this case a **List** is more efficient than a single **Variable** because the **Grayscale module** will be reporting more than one
sensor value. The **create list with** block will create separate **Variables** for each sensor, and put them into a List.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.7. Test Grayscale Module** **177**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.8 Color Detection**


PiCar-X is a self-driving car with a built-in camera, which allows Ezblock programs to utilize object detection and
color recognition code. In this section, Ezblock will be used to create a program for color detection.


**Note:** Before attempting this section, make sure that the Raspberry Pi Camera’s FFC cable is properly and securely
connected. For detailed instructions on securely connecting the FCC cable, please reference: _Assemble the PiCar-X_ .


In this program, Ezblock will first be told the Hue-Saturation-Value (HSV) space range of the color to be detected, then
utilize OpenCV to process the colors in the HSV range to remove the background noise, and finally, box the matching
color.


Ezblock includes 6 color models for PiCar-X, “red”, “orange”, “yellow”, “green”, “blue”, and “purple”. Color cards
have been prepared in the following PDF, and will need to be printed on a color printer.


   - `[PDF]Color Cards`


**178** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Note:** The printed colors may have a slightly different hue from the Ezblock color models due to printer toner differences, or the printed medium, such as a tan-colored paper. This can cause a less accurate color recognition.


**5.8. Color Detection** **179**


**SunFounder PiCar-X Kit**


**TIPS**


Drag the Video widget from the remote Control page, and it will generate a video monitor. For more information on
[how to use the Video widget, please reference the tutorial on Ezblock video here: How to Use the Video Function?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/use_video.html#video-latest)


Enable the video monitor by setting the **camera monitor** block to **on** . Note: Setting the **camera monitor** to **off** will
close the monitor, but object detection will still be available.


Use the **color detection** block to enable the color detection. Note: only one color can be detected at a time.


**180** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.9 Face Detection**


In addition to color detection, PiCar-X also includes a face detection function. In the following example the Joystick
widget is used to adjust the direction of the camera, and the number of faces will be displayed in the debug monitor.


[For more information on how to use the Video widget, please reference the tutorial on Ezblock video here: How to Use](https://docs.sunfounder.com/projects/ezblock3/en/latest/use_video.html#video-latest)
[the Video Function?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/use_video.html#video-latest)


**5.9. Face Detection** **181**


**SunFounder PiCar-X Kit**


**TIPS**


Set the **face detection** widget to **on** to enable facial detection.


These two blocks are used to adjust the orientation of the pan-tilt camera, similar to driving the PiCar-X in the _Remote_
_Control_ tutorial. As the value increases, the camera will rotate to the right, or upwards, a decreasing value will rotate
the camera right, or downwards.


**182** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


The image detection results are given through the of **detected face** block. Use the drop-down menu options to choose
between reading the coordinates, size, or number of results from the image detection function.


Use the **create text with** block to print the combination of **text** and of **detected face** data.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.9. Face Detection** **183**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


**184** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


Ready to explore and create with us? Click [] and join today!

### **5.10 Sound Effect**


PiCar-X has a built-in speaker that can be used for audio experiments. Ezblock allows users to enter text to make the
PiCar-X speak, or make specific sound effects. In this tutorial, the PiCar-X will make the sound of a gun firing after a
3-second countdown, using a do/while function.


**TIPS**


Use the **say** block with a **text** block to write a sentence for the PiCar-X to say. The **say** block can be used with text or
numbers.


The **number** block.


Using the **repeat** block will repeatedly execute the same statement, which reduces the size of the code.


The **mathematical operation** block can perform typical mathematical functions, such as ”+”, “-”, “x”, and “÷ “.


The play **sound effects - with volume - %** block has preset sound effects, such as a siren sound, a gun sound, and
others. The range of the volume can be set from 0 to 100.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


**5.10. Sound Effect** **185**


**SunFounder PiCar-X Kit**


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.11 Background Music**


In addition to programming the PiCar-X to play sound effects or text-to-speech (TTS), the PiCar-X will also play
background music. This project will also use a **Slider** widget for adjusting the music volume.


[• How to Use the Remote Control Function?](https://docs.sunfounder.com/projects/ezblock3/en/latest/remote.html#remote-control-latest)


For a detailed tutorial on Ezblocks remote control functions, please reference the _Remote Control_ tutorial.


**TIPS**


The **play background music** block will need to be added to the **Start** function. Use the drop-down menu to choose
different background music for the PiCar-X to play.


**186** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


The block **set background music volume to** will adjust the volume between the range of 0 to 100.


Drag a **Slider** bar from the **Remote Control** page to adjust music volume.


The **slider [A] get value** block will read the slider value. The example above has slider ‘A’ selected. If there are multiple
sliders, use the drop-down menu to select the appropriate one.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


**5.11. Background Music** **187**


**SunFounder PiCar-X Kit**


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.12 Say Hello**


This project will combine several functions from the preceding projects. The PiCar-X movement will be remotely
controlled, and the PiCar’s camera will be remotely controlled by using two joystick controllers. When PiCar recognizes
someone’s face, it will nod politely and then say “Hello!”.


[• How to Use the Video Function?](https://docs.sunfounder.com/projects/ezblock3/en/latest/use_video.html#video-latest)


[• How to Use the Remote Control Function?](https://docs.sunfounder.com/projects/ezblock3/en/latest/remote.html#remote-control-latest)


**TIPS**


The **if do** block is used to nod politely once the conditional judgment of “if” is true.


**188** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


The **conditional statements** block is used in conjunction with the **if do** block. The conditions can be “=”, “>”, “<”, ”
“, ” “, or ” “.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.12. Say Hello** **189**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**190** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.13 Music Car**


This project will turn the PiCar-X into a music car that will travel around your home, playing cheerful music. This
project will also show how the PiCar-X avoids hitting walls with the built-in ultrasonic sensor.


**TIPS**


To implement multiple conditional judgments, change the simple if do block into an if else do / else if do block. This
is done by clicking on the setting icon as shown above.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.13. Music Car** **191**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.14 Cliff Detection**


This project will use the **grayscale module** to prevent the PiCar-X from falling off a cliff while it is moving freely
around your home. This is an essential project for houses with staircases.


**TIPS**


**192** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


The **grayscale module** will be performing the same operation multiple times. To simplify the program, this project
introduces a **function** that will return a **list** variable to the **do forever** block.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**5.14. Cliff Detection** **193**


**SunFounder PiCar-X Kit**


**194** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**5.14. Cliff Detection** **195**


**SunFounder PiCar-X Kit**

### **5.15 Minecart**


Let’s make a minecart project! This project will use the Grayscale module to make the PiCar-X move forward along a
track. Use dark-colored tape to make a track on the ground as straight as possible, and not too curved. Some experimenting might be needed if the PiCar-X becomes derailed.


When moving along the track, the probes on the left and right sides of the Grayscale module will detect light-colored
ground, and the middle probe will detect the track. If the track has an arc, the probe on the left or right side of the
sensor will detect the dark-colored tape, and turn the wheels in that direction. If the minecart reaches the end of the
track or derails, the Grayscale module will no longer detect the dark-colored tape track, and the PiCar-X will come to
a stop.


**TIPS**


   - **Set ref to ()** block is used to set the grayscale threshold, you need to modify it according to the actual situation.
You can go ahead and run _Test Grayscale Module_ to see the values of the grayscale module on the white and
black surfaces, and fill in their middle values in this block.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**196** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**5.15. Minecart** **197**


**SunFounder PiCar-X Kit**


**198** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**5.15. Minecart** **199**


**SunFounder PiCar-X Kit**

### **5.16 Minecart Plus**


In this project, derailment recovery has been added to the _Minecart_ project to let the PiCar-X adapt and recover from
a more severe curve.


**TIPS**


1. Use another **to do something** block to allow the PiCar-X to back up and recover from a sharp curve. Note that
the new **to do something** function does not return any values, but is used just for reorienting the PiCar-X.


2. **Set ref to ()** block is used to set the grayscale threshold, you need to modify it according to the actual situation.
You can go ahead and run _Test Grayscale Module_ to see the values of the grayscale module on the white and
black surfaces, and fill in their middle values in this block.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**200** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**5.16. Minecart Plus** **201**


**SunFounder PiCar-X Kit**


**202** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**5.16. Minecart Plus** **203**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**204** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**

### **5.17 Bullfight**


Turn PiCar-X into an angry bull! Prepare a red cloth, such as a handkerchief, and become a Bullfighter. When the
PiCar-X chases after the red cloth, be careful not to get hit!


**Note:** This project is more advanced than the preceding projects. The PiCar-X will need to use the color detection
function to keep the camera facing towards the red cloth, then the body orientation will need to automatically adjust in
response to the direction that the camera is facing.


**TIPS**


Begin with adding the **color detection [red]** block to the **Start** widget to make the PiCar-X look for a red-colored
object. In the forever loop, add the **[width] of detected color** block to transform the input into an “object detection”
grid.


The “object detection” will output the detected coordinates in (x, y) values, based on the center point of the camera
image. The screen is divided into a 3x3 grid, as shown below, so if the red cloth is kept in the top left of the cameras’
image, the (x, y) coordinates will be (-1, 1).


The “object detection” will detect the Width and Height of the graphic. If multiple targets are identified, the dimensions
of the largest target will be recorded.


**5.17. Bullfight** **205**


**SunFounder PiCar-X Kit**


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


**206** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.18 Beware of Pedestrians**


This project will make the PiCar-X perform appropriate measures based on road conditions. While driving, the PiCar-X
will come to a complete stop if a pedestrian is detected in its path.


Once the program is running, hold a photo of a person in front of the PiCar-X. The Video Monitor will detect the
person’s face, and the PiCar-X will automatically come to a stop.


To simulate driving safety protocols, a judgment procedure is created that will send a **[count]** value to a **if do else** block.
The judgement procedure will look for a human face 10 times, and if a face does appear it will increment **[count]** by
+1. When **[count]** is larger than 3, the PiCar-X will stop moving.


[• How to Use the Remote Control Function?](https://docs.sunfounder.com/projects/ezblock3/en/latest/remote.html#remote-control-latest)


**EXAMPLE**


**5.18. Beware of Pedestrians** **207**


**SunFounder PiCar-X Kit**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


**208** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **5.19 Traffic Sign Detection**


In addition to color, face detection, PiCar-X can also do traffic sign detection.


Now let’s combine this traffic sign detection with the line following function. Let PiCar-X track the line, and when
you put the Stop sign in front of it, it will stop. When you place a Forward sign in front of it, it will continue to move
forward.


**TIPS**


1. PiCar will recognize 4 different traffic sign models included in the printable PDF below.


        - `[PDF]Traffic Sign Cards`


2. **Set ref to ()** block is used to set the grayscale threshold, you need to modify it according to the actual situation.
You can go ahead and run _Test Grayscale Module_ to see the values of the grayscale module on the white and
black surfaces, and fill in their middle values in this block.


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


**5.19. Traffic Sign Detection** **209**


**SunFounder PiCar-X Kit**


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**210** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**5.19. Traffic Sign Detection** **211**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**212** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**

### **5.20 Orienteering**


This project uses the remote control function to guide the PiCar-X through a competitive scavenger hunt!


First, set up either an obstacle course, or a maze, or even an empty room that the PiCar-X can drive through. Then,
randomly place six markers along the route, and put a color-card at each of the six markers for the PiCar-X to find.


The six color models for PiCar-X are: red, orange, yellow, green, blue and purple, and are ready to print from a colored
printer from the PDF below.


   - `[PDF]Color Cards`


**Note:** The printed colors may have a slightly different hue from the Ezblock color models due to printer toner differences, or the printed medium, such as a tan-colored paper. This can cause a less accurate color recognition.


The PiCar-X will be programmed to find three of the six colors in a random order, and will be using the TTS function
to announce which color to look for next.


The objective is to help the PiCar-X find each of the three colors in as short of a time as possible.


Place PiCar-X in the middle of the field and click the Button on the Remote Control page to start the game.


**5.20. Orienteering** **213**


**SunFounder PiCar-X Kit**


Take turns playing this game with friends to see who can help PiCar-X complete the objective the fastest!


**EXAMPLE**


**Note:**


[• You can write the program according to the following picture, please refer to the tutorial: How to Create a New](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)
[Project?.](https://docs.sunfounder.com/projects/ezblock3/en/latest/create_new.html#create-project-latest)


  - Or find the code with the same name on the **Examples** page of the EzBlock Studio and click **Run** or **Edit** directly.


**214** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**5.20. Orienteering** **215**


**SunFounder PiCar-X Kit**


**216** **Chapter 5. Play with Ezblock**


**SunFounder PiCar-X Kit**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**5.20. Orienteering** **217**


**SunFounder PiCar-X Kit**


**218** **Chapter 5. Play with Ezblock**


**CHAPTER**
