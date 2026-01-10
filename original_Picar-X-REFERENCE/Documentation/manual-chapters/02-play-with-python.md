### **TWO** **PLAY WITH PYTHON**


For novices and beginners wishing to program in Python, some basic Python skills and familiarity with the Raspberry
Pi OS are helpful. This section will guide you step by step — from setting up your Raspberry Pi, to moving PiCar-X,
to using computer vision, and finally adding voice and AI interaction.

### **2.1 1. Quick Guide on Python**


Learn how to set up your Raspberry Pi environment: install Raspberry Pi OS, configure Wi-Fi, and enable remote
access so you can run Python code easily. If you already know how to use Raspberry Pi and access its command line,
you may skip directly to the later parts.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.1.1 What Else Do You Need?**


Before we start playing with this kit, let’s prepare the essential hardware.


**7**


**SunFounder PiCar-X Kit**


**Required Components**


   - **Raspberry Pi**


The Raspberry Pi acts as the **brain**, handling all computing, sensing, and control tasks.


**– Compatible models** : Raspberry Pi 5, Raspberry Pi 4, 3, or Raspberry Pi Zero 2W


   - **Power Adapter**


Prepare a suitable power supply based on your Raspberry Pi model:


**– Raspberry Pi 5** : 5V 5A USB-C (recommended: official 27W PD power supply).


**– Raspberry Pi 4** : 5V 3A USB-C.


**8** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**– Raspberry Pi 3B/3B+** : 5V 2.5A Micro-USB.


**– Raspberry Pi Zero 2W** : 5V 2A Micro-USB.


Using a stable power source helps prevent undervoltage and ensures reliable operation.


   - **Micro SD Card**


The Raspberry Pi does not have a built-in hard drive. It boots and stores all files on a **Micro SD card** .


**–** Minimum: **16GB**


**–** Recommended: **32GB** for better stability


**–** Brand: Use reliable options such as **SanDisk** or **Samsung** to avoid read/write errors


**Optional Components**


Although not strictly required, the following peripherals will greatly improve your learning and debugging experience:


   - **Monitor (HDMI or TV)**


For beginners, we strongly recommend a display with an HDMI input, so you can easily configure Raspberry Pi
OS and run graphical programs.


**2.1. 1. Quick Guide on Python** **9**


**SunFounder PiCar-X Kit**


   - **HDMI Cable (Standard / Mini / Micro)**


Different Raspberry Pi models use different HDMI connectors, be sure to check your Pi model and prepare the
correct cable.


**– Raspberry Pi 4 / 5** : Micro HDMI


**– Raspberry Pi 3** : Standard HDMI


**– Raspberry Pi Zero 2W** : Mini HDMI


   - **Keyboard & Mouse**


Very useful during the initial setup of Raspberry Pi OS. Later, you may switch to remote access (SSH/VNC),
but for beginners we recommend preparing a basic USB or wireless set.


**Tips for Preparation**


  - If you purchased this kit, most accessories are included, but you still need to prepare the Raspberry Pi board,
Micro SD card, and power adapter separately.


  - Not sure what to buy? The most stable and universal choice is: **Raspberry Pi 4/5 (2GB) + Official Power**
**Supply + 32GB Micro SD card** .


**10** **Chapter 2. Play with Python**


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


**2.1.2 Installing the Operating System**


Before using your Raspberry Pi, you need to install **Raspberry Pi OS** onto a microSD card. This guide explains how
to do that using **Raspberry Pi Imager** in a simple, beginner-friendly way.


**Required Components**


  - A computer (Windows, macOS, or Linux)


  - A microSD card (16GB or larger; recommended brands: SanDisk, Samsung)


  - A microSD card reader


**2.1. 1. Quick Guide on Python** **11**


**SunFounder PiCar-X Kit**


**1. Install Raspberry Pi Imager**


1. Visit the official Raspberry Pi Imager download page: . Download the correct installer for your operating system.


2. Follow the installation prompts (language, install path, confirmation). After installation, launch **Raspberry Pi**
**Imager** from your desktop or applications menu.


**12** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**2. Install the OS to the microSD Card**


1. Insert your microSD card into your computer using a card reader. Back up any important data before proceeding.


2. When Raspberry Pi Imager opens, you will see the **Device** page. Select your Raspberry Pi model from the list
(e.g., Raspberry Pi 5, 4, 3, or Zero 2W).


**2.1. 1. Quick Guide on Python** **13**


**SunFounder PiCar-X Kit**


3. Go to the **OS** section and choose the recommended **Raspberry Pi OS (64-bit)** option.


4. In the **Storage** section, select your microSD card. For safety, unplug other USB drives so only the SD card
appears in the list.


**14** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. Click **Next** to continue to the customization step.


**Note:**


     - If you will connect a monitor, keyboard, and mouse directly to your Raspberry Pi, you may click **SKIP**
**CUSTOMISATION** .


     - If you plan to set up the Raspberry Pi _headless_ (Wi-Fi remote access), you must complete the customization
settings.


**2.1. 1. Quick Guide on Python** **15**


**SunFounder PiCar-X Kit**


**3. OS Customization Settings**


1. **Set Hostname**


     - Give your Raspberry Pi a unique hostname.


     - You can connect to it later using `hostname.local` .


**16** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


2. **Set Localisation**


     - Choose your capital city.


     - Imager will auto-complete the time zone and keyboard layout based on your selection, though you can
adjust them if needed. Select Next.


**2.1. 1. Quick Guide on Python** **17**


**SunFounder PiCar-X Kit**


3. **Set Username & Password**


Create a user account for your Raspberry Pi.


4. **Configure Wi-Fi**


     - Enter your Wi-Fi **SSID** (network name) and **password** .


     - Your Raspberry Pi will automatically connect on first boot.


**18** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. **Enable SSH (Optional but Recommended)**


     - Enabling SSH allows you to remotely log in from your computer.


     - You may log in using your username/password or configure SSH keys.


**2.1. 1. Quick Guide on Python** **19**


**SunFounder PiCar-X Kit**


6. **Enable Raspberry Pi Connect (Optional)**


Raspberry Pi Connect allows you to access your Raspberry Pi desktop from a web browser.


     - Turn on **Raspberry Pi Connect**, then click **OPEN RASPBERRY PI CONNECT** .


     - The Raspberry Pi Connect website will open in your default browser. Log in to your Raspberry Pi ID
account, or sign up if you don’t have one yet.


     - On the **New auth key** page, create your one-time auth key.


**–** If your Raspberry Pi ID account isn’t part of any organisation, select **Create auth key and launch**
**Raspberry Pi Imager** .


**–** If you belong to one or more organisations, choose one, then create the key and launch Imager.


**–** Make sure to power on your Raspberry Pi and connect it to the internet before the key expires.


**20** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


     - Your browser may ask to open Raspberry Pi Imager — allow it.


**–** Imager will open on the Raspberry Pi Connect tab, showing the authentication token.


**–** If the token doesn’t transfer automatically, open the **Having trouble?** section on the Raspberry Pi
Connect page, copy the token, and paste it into Imager manually.


**4. Write the OS Image**


1. Review all settings and click **WRITE** .


**2.1. 1. Quick Guide on Python** **21**


**SunFounder PiCar-X Kit**


2. If the card already contains data, Raspberry Pi Imager will show a warning that all data on the device will be
erased. Double-check that you selected the correct drive, then click **I UNDERSTAND, ERASE AND WRITE**
to continue.


3. Wait for the writing and verification to finish. When it is done, Raspberry Pi Imager will show **Write complete!**
and a summary of your choices. The storage device will be ejected automatically so you can remove it safely.


**22** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


4. Remove the microSD card and insert it into the slot on the underside of your Raspberry Pi. Your Raspberry Pi
is now ready to boot with the new OS!


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


**2.1. 1. Quick Guide on Python** **23**


**SunFounder PiCar-X Kit**


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.1.3 Power Supply for Raspberry Pi (Important)**


**Charge**


Insert the battery cable. Next, insert the USB-C cable to charge the battery. You will need to provide your own charger;
we recommend a 5V 3A charger, or your commonly used smartphone charger will suffice.


**Note:** Connect an external Type-C power source to the Type-C port on the robot hat; it will immediately start charging
the battery, and a red indicator light will illuminate.When the battery is fully charged, the red light will automatically
turn off.


**24** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**Power ON**


Turn on the power switch. The Power indicator light and the battery level indicator light will illuminate.


Wait for a few seconds, and you will hear a slight beep, indicating that the Raspberry Pi has successfully booted.


**Note:** If both battery level indicator lights are off, please charge the battery. When you need extended programming
or debugging sessions, you can keep the Raspberry Pi operational by inserting the USB-C cable to charge the battery
simultaneously.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.1. 1. Quick Guide on Python** **25**


**SunFounder PiCar-X Kit**


**2.1.4 Set Up Your Raspberry Pi**


To begin programming and controlling your Raspberry Pi, you first need to access it. This guide describes two common
methods:


  - Using a monitor, keyboard, and mouse


  - Setting up a headless (no-screen) connection for remote access


**Note:** The Raspberry Pi Zero 2W installed on the robot is not easy to connect to a screen. We recommend using the
**headless setup** method.


**If You Have a Screen**


**Required Components**


  - Raspberry Pi


  - Official Power Supply


  - MicroSD Card


  - HDMI Cable (For Raspberry Pi 4/5, use **HDMI0**, the port nearest the power connector.)


  - Monitor


  - Keyboard and Mouse


**Steps**


1. Insert the microSD card into your Raspberry Pi.


2. Connect the keyboard, mouse, and monitor.


3. Power on your Raspberry Pi.


4. After booting, the Raspberry Pi OS desktop will appear.


**26** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. Open a **Terminal** to enter commands.


**2.1. 1. Quick Guide on Python** **27**


**SunFounder PiCar-X Kit**


**If You Have No Screen (Headless)**


Without a monitor, you can configure and log in to your Raspberry Pi remotely. This is the most convenient method
for most users.


**Required Components**


  - Raspberry Pi


  - Official Power Supply


  - MicroSD Card


  - A computer on the same network


**Tips**


  - Make sure you have completed all settings described in _3. OS Customization Settings_ when installing the system
with Raspberry Pi Imager.


  - Ensure that your Raspberry Pi and your computer are on the same local network.


  - For best stability, use Ethernet if available.


**Connect via SSH**


1. Open a terminal on your computer (Windows: **PowerShell** ; macOS/Linux: **Terminal** ) and connect to your
Raspberry Pi:





2. Alternatively, locate your Pi’s IP address from your router’s DHCP list and connect with:





3. On first login, type `yes` to confirm the SSH certificate.


4. Enter the password you configured in Raspberry Pi Imager. (Nothing appears while typing—this is normal.)


5. After login, you now have full command-line access.


**28** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**Troubleshooting**


   - **ssh: Could not resolve hostname ...**


**–** Make sure the hostname is correct.


**–** Try connecting using the Pi’s IP address.


   - **The term ‘ssh’ is not recognized... (Windows)**


**–** OpenSSH is not installed. Install it manually or use a third-party SSH client.


**–** See _Install OpenSSH via PowerShell_ or _PuTTY_ .


   - **Permission denied (publickey,password)**


**–** Ensure you are using the username and password created in Raspberry Pi Imager.


   - **Connection refused**


**–** Wait 1–2 minutes after powering on.


**–** Confirm that SSH was enabled in Raspberry Pi Imager.


**Graphical Remote Access Options**


If you prefer a graphical interface:


   - _Remote Desktop_ : Enable **VNC (Virtual Network Computing)** for a full desktop experience on your Pi.


  - : Use Raspberry Pi Connect for secure remote access from anywhere, directly in a browser.


Now you can control your Raspberry Pi without a monitor, either through SSH for command-line operations, or with
VNC / Raspberry Pi Connect for a graphical desktop experience.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**2.1. 1. Quick Guide on Python** **29**


**SunFounder PiCar-X Kit**


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.1.5 Install All the Modules (Important)**


1. **Prepare the system**


Make sure your Raspberry Pi is connected to the Internet, then update the system:





**Note:** If you are using Raspberry Pi OS Lite, install the required Python 3 packages first:

```
 sudo apt install git python3-pip python3-setuptools python3-smbus

```

2. **Install robot-hat**


Download and install the `robot-hat` module:





3. **Install vilib**


Download and install the `vilib` module:





4. **Install picar-x**


Download and install the `picar-x` module:





This step may take a little while. Please be patient.


**30** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. **Enable sound (I2S amplifier)**


To enable audio output, run the `i2samp.sh` script to install the required I2S amplifier components:





Follow the on-screen prompts by typing `y` and pressing Enter to continue, run `/dev/zero` in the background,
and restart the Picar-X.


**Note:** If there is no sound after restarting, try running the `i2samp.sh` script several times.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.1.6 Servo Adjust(Important)**


**Note:** If your Robot HAT is version V44 or higher (with the speaker located at the top of the board) and includes an
onboard **Zero** button, you can skip this step and simply press the **Zero** button to activate the servo zeroing program.


**2.1. 1. Quick Guide on Python** **31**


**SunFounder PiCar-X Kit**


The angle range of the servo is -90~90, but the angle set at the factory is random, maybe 0°, maybe 45°; if we assemble
it with such an angle directly, it will lead to a chaotic state after the robot runs the code, or worse, it will cause the servo
to block and burn out.


So here we need to set all the servo angles to 0° and then install them, so that the servo angle is in the middle, no matter
which direction to turn.


1. To ensure that the servo has been properly set to 0°, first insert the servo arm into the servo shaft and then gently
rotate the rocker arm to a different angle. This servo arm is just to allow you to clearly see that the servo is
rotating.


2. Now, run `servo_zeroing.py` in the `example/` folder.





**32** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


3. Next, plug the servo cable into the P11 port as follows, at the same time you will see the servo arm rotate to a
position(This is the 0° position, which is a random location and may not be vertical or parallel.).

```
     python/img/Z_P11.JPG

```

4. Now, remove the servo arm, ensuring the servo wire remains connected, and do not turn off the power. Then
continue the assembly following the paper instructions.


**Note:**


  - Do not unplug this servo cable before fixing it with the servo screw, you can unplug it after fixing it.


  - Do not rotate the servo while it is powered on to avoid damage; if the servo shaft is not inserted at the right angle,
pull the servo out and reinsert it.


  - Before assembling each servo, you need to plug the servo cable into P11 and turn on the power to set its angle to
0°.

### **2.2 2. Basic Movement**


After assembling your PiCar-X, start with simple movement programs. You will learn how to control the motors, drive
forward/backward, turn, and use basic sensors for avoiding obstacles or following lines.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.2. 2. Basic Movement** **33**


**SunFounder PiCar-X Kit**


**2.2.1 1. Calibrating the PiCar-X**


**Calibrate Motors & Servo**


Some servo angles may be slightly tilted due to possible deviations during PiCar-X installation or limitations of the
servos themselves, so you can calibrate them.


Of course, you can skip this chapter if you think the assembly is perfect and doesn’t require calibration.


1. Run the `calibration.py` .





2. After running the code, you will see the following interface displayed in the terminal.


3. The `R` key is used to test if the 3 servos are working properly.


4. Press the number key `1` to select the front wheel servo, and then press the `W/S` key to let the front wheel looks as
forward as possible without skewing left and right.


**34** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. Press the number key `2` to select the **Pan servo**, then press the `W/S` key to make the pan/tilt platform look straight
ahead and not tilt left or right.


6. Press the number key `3` to select the **tilt servo**, then press the `W/S` key to make the pan/tilt platform look straight
ahead and not tilt up and down.


**2.2. 2. Basic Movement** **35**


**SunFounder PiCar-X Kit**


7. Since the wiring of the motors may be reversed during installation, you can press `E` to test whether the car can
move forward normally. If not, use the number keys `4` and `5` to select the left and right motors, then press the `Q`
key to calibrate the rotation direction.


8. When the calibration is completed, press the `Spacebar` to save the calibration parameters. There will be a prompt
to enter `y` to confirm, and then press `Ctrl+C` to exit the program to complete the calibration.


**36** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**Calibrate Grayscale Module**


Due to varying environmental conditions and lighting situations, the preset parameters for the greyscale module might
not be optimal. You can fine-tune these settings through this program to achieve better results.


1. Lay down a strip of black electrical tape, about 15cm long, on a light-colored floor. Center your PiCar-X so that
it straddles the tape. In this setup, the middle sensor of the greyscale module should be directly above the tape,
while the two flanking sensors should hover over the lighter surface.


2. Run the code.





3. After running the code, you will see the following interface displayed in the terminal.


**2.2. 2. Basic Movement** **37**


**SunFounder PiCar-X Kit**


4. Press the “Q” key to initiate the greyscale calibration. You’ll then observe the PiCar-X make minor movements
to both the left and the right. During this process, each of the three sensors should sweep across the electrical
tape at least once.


5. Additionally, you will notice three pairs of significantly different values appearing in the “threshold value” section, while the “line reference” will display two intermediate values, each representing the average of one of
these pairs.


**38** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


6. Next, suspend the PiCar-X in mid-air (or position it over a cliff edge) and press the “E” key. You’ll observe that
the “cliff reference” values are also updated accordingly.


7. Once you’ve verified that all the values are accurate, press the “space” key to save the data. You can then exit the
program by pressing Ctrl+C.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.2.2 2. Let PiCar-X Move**


This is the first project, let’s test the basic movement of Picar-X.


**Run the Code**





After running the code, PiCar-X will move forward, turn in an S-shape, stop and shake its head.


**2.2. 2. Basic Movement** **39**


**SunFounder PiCar-X Kit**


**Code**


**Note:** You can **Modify/Reset/Copy/Run/Stop** the code below. But before that, you need to go to source code path
like `picar-x/example` . After modifying the code, you can run it directly to see the effect.



**How it works?**


The basic functionality of PiCar-X is in the `picarx` module, Can be used to control steering gear and wheels, and will
make the PiCar-X move forward, turn in an S-shape, or shake its head.


Now, the libraries to support the basic functionality of PiCar-X are imported. These lines will appear in all the examples


**40** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**



that involve PiCar-X movement.





The following function with the `for` loop is then used to make PiCar-X move forward, change directions, and move
the camera’s pan/tilt.






   - `forward()` : Orders the PiCar-X go forward at a given `speed` .


   - `set_dir_servo_angle` : Turns the Steering servo to a specific `angle` .


   - `set_cam_pan_angle` : Turns the Pan servo to a specific `angle` .


   - `set_cam_tilt_angle` : Turns the Tilt servo to a specific `angle` .


**2.2. 2. Basic Movement** **41**


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


**42** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


**2.2.3 3. Keyboard Control**


In this project, we will learn how to use the keyboard to remotely control the PiCar-X. You can control the PiCar-X to
move forward, backward, left, and right.


**Run the Code**





Press keys on keyboard to control PiCar-X!


  - w: Forward


  - a: Turn left


  - s: Backward


  - d: Turn right


  - i: Head up


  - k: Head down


  - j: Turn head left


  - l: Turn head right


  - ctrl + c: Press twice to exit the program


**Code**

```
from picarx import Picarx
from time import sleep
import readchar

manual = '''
Press keys on keyboard to control PiCar-X!
  w: Forward
  a: Turn left
  s: Backward
  d: Turn right
  i: Head up
  k: Head down
  j: Turn head left
  l: Turn head right
  ctrl+c: Quit
'''

def show_info():
  print("\033[H\033[J",end='') # clear terminal windows
  print(manual)

if __name__ == "__main__":
  try:
    pan_angle = 0
    tilt_angle = 0
    px = Picarx()
```

(continues on next page)


**2.2. 2. Basic Movement** **43**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
    show_info()
    while True:
      key = readchar.readkey()
      key = key.lower()
      if key in('wsadikjl'):
        if 'w' == key:
          px.set_dir_servo_angle(0)
          px.forward(80)
        elif 's' == key:
          px.set_dir_servo_angle(0)
          px.backward(80)
        elif 'a' == key:
          px.set_dir_servo_angle(-35)
          px.forward(80)
        elif 'd' == key:
          px.set_dir_servo_angle(35)
          px.forward(80)
        elif 'i' == key:
          tilt_angle+=5
          if tilt_angle>35:
             tilt_angle=35
        elif 'k' == key:
          tilt_angle-=5
          if tilt_angle<-35:
             tilt_angle=-35
        elif 'l' == key:
          pan_angle+=5
          if pan_angle>35:
             pan_angle=35
        elif 'j' == key:
          pan_angle-=5
          if pan_angle<-35:
             pan_angle=-35

        px.set_cam_tilt_angle(tilt_angle)
        px.set_cam_pan_angle(pan_angle)
        show_info()
        sleep(0.5)
        px.forward(0)

      elif key == readchar.key.CTRL_C:
        print("\n Quit")
        break

  finally:
    px.set_cam_tilt_angle(0)
    px.set_cam_pan_angle(0)
    px.set_dir_servo_angle(0)
    px.stop()
    sleep(.2)

```

**How it works?**


**44** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


PiCar-X should take appropriate action based on the keyboard characters read. The `lower()` function converts upper
case characters into lower case characters, so that the letter remains valid regardless of case.



**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.2.4 4. Obstacle Avoidance**


In this project, PiCar-X will detect obstacles in front of it while moving forward, and when the obstacles are too close,
it will change the direction of moving forward.


**Run the Code**





**2.2. 2. Basic Movement** **45**


**SunFounder PiCar-X Kit**


After running the code, PiCar-X will walk forward.


If it detects that the distance of the obstacle ahead is less than 20cm, it will go backward.


If there is an obstacle within 20 to 40cm, it will turn left.


If there is no obstacle in the direction after turning left or the obstacle distance is greater than 25cm, it will continue to
move forward.


**Code**


**Note:** You can **Modify/Reset/Copy/Run/Stop** the code below. But before that, you need to go to source code path
like `picar-x/example` . After modifying the code, you can run it directly to see the effect.



**How it works?**


  - Importing the Picarx Module and Initializing Constants:


This section of the code imports the `Picarx` class from the `picarx` module, which is essential for controlling the Picarx robot. Constants like `POWER`, `SafeDistance`, and `DangerDistance` are defined,
which will be used later in the script to control the robot’s movement based on distance measurements.


**46** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**

```
   from picarx import Picarx
   import time

   POWER = 50
   SafeDistance = 40 # > 40 safe
   DangerDistance = 20 # > 20 && < 40 turn around,
   # < 20 backward

```

- Main Function Definition and Ultrasonic Sensor Reading:


The `main` function is where the Picarx robot is controlled. An instance of `Picarx` is created, which
activates the robot’s functionalities. The code enters an infinite loop, constantly reading the distance
from the ultrasonic sensor. This distance is used to determine the robot’s movement.

```
   def main():
   try:
   px = Picarx()

     while True:
       distance = round(px.ultrasonic.read(), 2)
       # [Rest of the logic]

```

- Movement Logic Based on Distance:


The robot’s movement is controlled based on the `distance` read from the ultrasonic sensor. If
the `distance` is greater than `SafeDistance`, the robot moves forward. If the distance is between
`DangerDistance` and `SafeDistance`, it slightly turns and moves forward. If the `distance` is less
than `DangerDistance`, the robot reverses while turning in the opposite direction.






- Safety and Cleanup with the ‘finally’ Block:


The `try...finally` block ensures safety by stopping the robot’s motion in case of an interruption
or error. This is a crucial part for preventing uncontrollable behavior of the robot.






  - Execution Entry Point:


The standard Python entry point `if __name__ == "__main__":` is used to run the main function
when the script is executed as a standalone program.


**2.2. 2. Basic Movement** **47**


**SunFounder PiCar-X Kit**





In summary, the script uses the Picarx module to control a robot, utilizing an ultrasonic sensor for distance measurement.
The robot’s movement is adapted based on these measurements, ensuring safe operation through careful control and a
safety mechanism in the finally block.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.2.5 5. Cliff Detection**


Let us give PiCar-X a little self-protection awareness and let it learn to use its own grayscale module to avoid rushing
down the cliff.


In this example, the car will be dormant. If you push it to a cliff, it will be awakened urgently, then back up.


**Run the Code**





**Code**


**Note:** You can **Modify/Reset/Copy/Run/Stop** the code below. But before that, you need to go to source code path
like `picar-x/example` . After modifying the code, you can run it directly to see the effect.

```
from picarx import Picarx
from time import sleep

px = Picarx()
```

_`# px = Picarx(grayscale_pins=[`_ _'_ _`A0`_ _'_ _`,`_ _'_ _`A1`_ _'_ _`,`_ _'_ _`A2`_ _'_ _`])`_
```
# manual modify reference value
px.set_cliff_reference([200, 200, 200])

last_state = "safe"

if __name__ == '__main__':
  try:
    while True:
```

(continues on next page)


**48** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
      gm_val_list = px.get_grayscale_data()
      gm_state = px.get_cliff_status(gm_val_list)
      # print("cliff status is: %s" % gm_state)

      if gm_state is False:
        state = "safe"
        px.stop()
      else:
        state = "danger"
        px.backward(80)
        if last_state == "safe":
          sleep(0.1)

      last_state = state

  except KeyboardInterrupt:
    print("\nKeyboardInterrupt: stop and exit")

  finally:
    px.stop()
    sleep(0.1)

```

**How it works?**


The function to detect the cliff looks like this:


   - `get_grayscale_data()` : This method directly outputs the readings of the three sensors, from right to left. The
brighter the area, the larger the value obtained.


   - `get_cliff_status(gm_val_list)` : This method compares the readings from the three probes and outputs a
result. If the result is true, it is detected that there is a cliff in front of the car.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.2. 2. Basic Movement** **49**


**SunFounder PiCar-X Kit**


**2.2.6 6. Line Tracking**


This project will use the Grayscale module to make the PiCar-X move forward along a line. Use dark-colored tape to
make a line as straight as possible, and not too curved. Some experimenting might be needed if the PiCar-X is derailed.


**Run the Code**





After running the code, PiCar-X will move forward along a line.


**Code**


**Note:** You can **Modify/Reset/Copy/Run/Stop** the code below. But before that, you need to go to source code path
like `picar-x/example` . After modifying the code, you can run it directly to see the effect.



**50** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)





**How it works?**


This Python script controls a Picarx robot car using grayscale sensors for navigation. Here’s a breakdown of its main
components:


  - Import and Initialization:


The script imports the Picarx class for controlling the robot car and the sleep function from the time
module for adding delays.


An instance of Picarx is created, and there’s a commented line showing an alternative initialization
with specific grayscale sensor pins.

```
     from picarx import Picarx
     from time import sleep

```

(continues on next page)


**2.2. 2. Basic Movement** **51**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
     px = Picarx()

```

  - Configuration and Global Variables:


`current_state`, `px_power`, `offset`, and `last_state` are global variables used to track and control
the car’s movement. `px_power` sets the motor power, and `offset` is used for adjusting the steering
angle.






- `outHandle` Function:


This function is called when the car needs to handle an ‘out of line’ scenario.


It adjusts the car’s direction based on `last_state` and checks the grayscale sensor values to determine
the new state.






- `get_status` Function:


It interprets the grayscale sensor data ( `val_list` ) to determine the car’s navigation state.


The car’s state can be ‘forward’, ‘left’, ‘right’, or ‘stop’, based on which sensor detects the line.










  - Main Loop:


**52** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


The `while True` loop continuously checks the grayscale data and adjusts the car’s movement accordingly.


Depending on the `gm_state`, it sets the steering angle and movement direction.




- Safety and Cleanup:


The `try...finally` block ensures the car stops when the script is interrupted or finished.





In summary, the script uses grayscale sensors to navigate the Picarx robot car. It continuously reads the sensor data
to determine the direction and adjusts the car’s movement and steering accordingly. The outHandle function provides
additional logic for situations where the car needs to adjust its path significantly.

### **2.3 3. Computer Vision**


Give your PiCar-X the ability to see using its camera. This section covers fun vision-based projects such as face
tracking, recording, object interactions, and controlling the car via video or a mobile app.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


**2.3. 3. Computer Vision** **53**


**SunFounder PiCar-X Kit**


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.3.1 7. Computer Vision**


This project will officially enter the field of computer vision!


**Run the Code**





**View the Image**


After the code runs, the terminal will display the following prompt:

```
No desktop !
* Serving Flask app "vilib.vilib" (lazy loading)
* Environment: production
WARNING: Do not use the development server in a production environment.
Use a production WSGI server instead.
* Debug mode: off
* Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

```

Then you can enter `http://<your IP>:9000/mjpg` in the browser to view the video screen. such as: `https://`
```
192.168.18.113:9000/mjpg

```

After the program runs, you will see the following information in the final:


  - Input key to call the function!


  - q: Take photo


  - 1: Color detect : red


  - 2: Color detect : orange


  - 3: Color detect : yellow


  - 4: Color detect : green


  - 5: Color detect : blue


  - 6: Color detect : purple


  - 0: Switch off Color detect


  - r: Scan the QR code


  - f: Switch ON/OFF face detect


  - s: Display detected object information


**54** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


Please follow the prompts to activate the corresponding functions.


   - **Take Photo**


Type `q` in the terminal and press Enter. The picture currently seen by the camera will be saved (if the
color detection function is turned on, the mark box will also appear in the saved picture). You can see
these photos from the `/home/{username}/Pictures/` directory of the Raspberry Pi. You can use
tools such as _FileZilla Software_ to transfer photos to your PC.


   - **Color Detect**


Entering a number between `1~6` will detect one of the colors in “red, orange, yellow, green, blue,
purple”. Enter `0` to turn off color detection.


**Note:** You can download and print the `PDF Color Cards` for color detection.


   - **Face Detect**


Type `f` to turn on face detection.


**2.3. 3. Computer Vision** **55**


**SunFounder PiCar-X Kit**


   - **QR Code Detect**


Enter `r` to open the QR code recognition. No other operations can be performed before the QR code
is recognized. The decoding information of the QR code will be printed in the terminal.


   - **Display Information**


**56** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


Entering `s` will print the information of the face detection (and color detection) target in the terminal.
Including the center coordinates (X, Y) and size (Weight, height) of the measured object.


**Code**

```
from pydoc import text
from vilib import Vilib
from time import sleep, time, strftime, localtime
import threading
import readchar
import os

flag_face = False
flag_color = False
qr_code_flag = False

manual = '''
Input key to call the function!
  q: Take photo
  1: Color detect : red
  2: Color detect : orange
  3: Color detect : yellow
  4: Color detect : green
  5: Color detect : blue
  6: Color detect : purple
  0: Switch off Color detect
  r: Scan the QR code
  f: Switch ON/OFF face detect
  s: Display detected object information
'''

color_list = ['close', 'red', 'orange', 'yellow',
    'green', 'blue', 'purple',
]

def face_detect(flag):
  print("Face Detect:" + str(flag))
  Vilib.face_detect_switch(flag)

def qrcode_detect():
  global qr_code_flag
  if qr_code_flag == True:
    Vilib.qrcode_detect_switch(True)
    print("Waitting for QR code")

  text = None
  while True:
    temp = Vilib.detect_obj_parameter['qr_data']
    if temp != "None" and temp != text:
      text = temp
      print('QR code: %s '%text)
    if qr_code_flag == False:
      break
```

(continues on next page)


**2.3. 3. Computer Vision** **57**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
    sleep(0.5)
  Vilib.qrcode_detect_switch(False)

def take_photo():
  _time = strftime('%Y-%m- %d -%H-%M-%S',localtime(time()))
  name = 'photo_ %s '%_time
  username = os.getlogin()

  path = f"/home/ { username } /Pictures/"
  Vilib.take_photo(name, path)
  print('photo save as %s%s .jpg'%(path,name))

def object_show():
  global flag_color, flag_face

  if flag_color is True:
    if Vilib.detect_obj_parameter['color_n'] == 0:
      print('Color Detect: None')
    else:
      color_coodinate = (Vilib.detect_obj_parameter['color_x'],Vilib.detect_obj_
```

_˓→_ `parameter['color_y'])`
```
      color_size = (Vilib.detect_obj_parameter['color_w'],Vilib.detect_obj_
```

_˓→_ `parameter['color_h'])`
```
      print("[Color Detect] ","Coordinate:",color_coodinate,"Size",color_size)

  if flag_face is True:
    if Vilib.detect_obj_parameter['human_n'] == 0:
      print('Face Detect: None')
    else:
      human_coodinate = (Vilib.detect_obj_parameter['human_x'],Vilib.detect_obj_
```

_˓→_ `parameter['human_y'])`
```
      human_size = (Vilib.detect_obj_parameter['human_w'],Vilib.detect_obj_
```

_˓→_ `parameter['human_h'])`
```
      print("[Face Detect] ","Coordinate:",human_coodinate,"Size",human_size)

def main():
  global flag_face, flag_color, qr_code_flag
  qrcode_thread = None

  Vilib.camera_start(vflip=False,hflip=False)
  Vilib.display(local=True,web=True)
  print(manual)

  while True:
    # readkey
    key = readchar.readkey()
    key = key.lower()
    # take photo
    if key == 'q':

```

(continues on next page)


**58** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)



**How it works?**


The first thing you need to pay attention to here is the following function. These two functions allow you to start the
camera.





Functions related to “object detection”:


   - `Vilib.face_detect_switch(True)` : Switch ON/OFF face detection


   - `Vilib.color_detect(color)` : For color detection, only one color detection can be performed at the same
time. The parameters that can be input are: `"red"`, `"orange"`, `"yellow"`, `"green"`, `"blue"`, `"purple"`


   - `Vilib.color_detect_switch(False)` : Switch OFF color detection


**2.3. 3. Computer Vision** **59**


**SunFounder PiCar-X Kit**


   - `Vilib.qrcode_detect_switch(False)` : Switch ON/OFF QR code detection, Returns the decoded data of
the QR code.


   - `Vilib.gesture_detect_switch(False)` : Switch ON/OFF gesture detection


   - `Vilib.traffic_sign_detect_switch(False)` : Switch ON/OFF traffic sign detection


The information detected by the target will be stored in the `detect_obj_parameter = Manager().dict()` dictionary.


In the main program, you can use it like this:

```
Vilib.detect_obj_parameter['color_x']

```

The keys of the dictionary and their uses are shown in the following list:


   - `color_x` : the x value of the center coordinate of the detected color block, the range is 0~320


   - `color_y` : the y value of the center coordinate of the detected color block, the range is 0~240


   - `color_w` : the width of the detected color block, the range is 0~320


   - `color_h` : the height of the detected color block, the range is 0~240


   - `color_n` : the number of detected color patches


   - `human_x` : the x value of the center coordinate of the detected human face, the range is 0~320


   - `human_y` : the y value of the center coordinate of the detected face, the range is 0~240


   - `human_w` : the width of the detected human face, the range is 0~320


   - `human_h` : the height of the detected face, the range is 0~240


   - `human_n` : the number of detected faces


   - `traffic_sign_x` : the center coordinate x value of the detected traffic sign, the range is 0~320


   - `traffic_sign_y` : the center coordinate y value of the detected traffic sign, the range is 0~240


   - `traffic_sign_w` : the width of the detected traffic sign, the range is 0~320


   - `traffic_sign_h` : the height of the detected traffic sign, the range is 0~240


   - `traffic_sign_t` : the content of the detected traffic sign, the value list is _[‘stop’,’right’,’left’,’forward’]_


   - `gesture_x` : The center coordinate x value of the detected gesture, the range is 0~320


   - `gesture_y` : The center coordinate y value of the detected gesture, the range is 0~240


   - `gesture_w` : The width of the detected gesture, the range is 0~320


   - `gesture_h` : The height of the detected gesture, the range is 0~240


   - `gesture_t` : The content of the detected gesture, the value list is _[“paper”,”scissor”,”rock”]_


   - `qr_date` : the content of the QR code being detected


   - `qr_x` : the center coordinate x value of the QR code to be detected, the range is 0~320


   - `qr_y` : the center coordinate y value of the QR code to be detected, the range is 0~240


   - `qr_w` : the width of the QR code to be detected, the range is 0~320


   - `qr_h` : the height of the QR code to be detected, the range is 0~320


**60** **Chapter 2. Play with Python**


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


**2.3.2 8. Stare at You**


This project is also based on the _7. Computer Vision_ project, with the addition of face detection algorithms.


When you appear in front of the camera, it will recognize your face and adjust its gimbal to keep your face in the center
of the frame.


You can view the screen at `http://<your IP>:9000/mjpg` .


**Run the Code**





When the code is run, the car’s camera will always be staring at your face.


**Code**

```
from picarx import Picarx
from time import sleep
from vilib import Vilib

px = Picarx()

def clamp_number(num,a,b):
  return max(min(num, max(a, b)), min(a, b))

def main():
  Vilib.camera_start()
  Vilib.display()
  Vilib.face_detect_switch(True)
  x_angle =0
  y_angle =0
  while True:
    if Vilib.detect_obj_parameter['human_n']!=0:
      coordinate_x = Vilib.detect_obj_parameter['human_x']
      coordinate_y = Vilib.detect_obj_parameter['human_y']

      # change the pan-tilt angle for track the object
```

(continues on next page)


**2.3. 3. Computer Vision** **61**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
      x_angle +=(coordinate_x*10/640)-5
      x_angle = clamp_number(x_angle,-35,35)
      px.set_cam_pan_angle(x_angle)

      y_angle -=(coordinate_y*10/480)-5
      y_angle = clamp_number(y_angle,-35,35)
      px.set_cam_tilt_angle(y_angle)

      sleep(0.05)

    else :
      pass
      sleep(0.05)

if __name__ == "__main__":
  try:
  main()

  finally:
    px.stop()
    print("stop and exit")
    sleep(0.1)

```

**How it works?**


These lines of code in `while True` make the camera follow the face.



1. Check if there is a detected human face

```
     Vilib.detect_obj_parameter['human_n'] != 0

```

2. If a human face is detected, obtain the coordinates ( `coordinate_x` and `coordinate_y` ) of the detected face.


3. Calculate new pan and tilt angles ( `x_angle` and `y_angle` ) based on the detected face’s position and adjust them
to follow the face.


4. Limit the pan and tilt angles within the specified range using the `clamp_number` function.


5. Set the camera’s pan and tilt angles using `px.set_cam_pan_angle()` and `px.set_cam_tilt_angle()` .


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!


**62** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.3.3 9. Record Video**


This example will guide you how to use the recording function.


**Run the Code**





After the code runs, you can enter `http://<your IP>:9000/mjpg` in the browser to view the video screen. such as:
```
http://192.168.18.113:9000/mjpg

```

Recording can be stopped or started by pressing the keys on the keyboard.


  - Press `q` to begin recording or pause/continue, `e` to stop recording or save.


  - If you want to exit the program, press `ctrl+c` .


**Code**





**2.3. 3. Computer Vision** **63**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
def main():
  rec_flag = 'stop' # start,pause,stop
  vname = None
  username = os.getlogin()

  Vilib.rec_video_set["path"] = f"/home/ { username } /Videos/" # set path

  Vilib.camera_start(vflip=False,hflip=False)
  Vilib.display(local=True,web=True)
  sleep(0.8) # wait for startup

  print(manual)
  while True:
    # read keyboard
    key = readchar.readkey()
    key = key.lower()
    # start,pause
    if key == 'q':
      key = None
      if rec_flag == 'stop':
        rec_flag = 'start'
        # set name
        vname = strftime("%Y-%m- %d -%H.%M.%S", localtime())
        Vilib.rec_video_set["name"] = vname
        # start record
        Vilib.rec_video_run()
        Vilib.rec_video_start()
        print_overwrite('rec start ...')
      elif rec_flag == 'start':
        rec_flag = 'pause'
        Vilib.rec_video_pause()
        print_overwrite('pause')
      elif rec_flag == 'pause':
        rec_flag = 'start'
        Vilib.rec_video_start()
        print_overwrite('continue')
    # stop
    elif key == 'e' and rec_flag != 'stop':
      key = None
      rec_flag = 'stop'
      Vilib.rec_video_stop()
      print_overwrite("The video saved as %s%s .avi"%(Vilib.rec_video_set["path"],
```

_˓→_ `vname),end='\n')`
```
    # quit
    elif key == readchar.key.CTRL_C:
      Vilib.camera_close()
      print('\nquit')
      break

    sleep(0.1)

if __name__ == "__main__":

```

(continues on next page)


**64** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
  main()

```

**How it works?**


Functions related to recording include the following:


   - `Vilib.rec_video_run(video_name)` : Started the thread to record the video. `video_name` is the name of
the video file, it should be a string.


   - `Vilib.rec_video_start()` : Start or continue video recording.


   - `Vilib.rec_video_pause()` : Pause recording.


   - `Vilib.rec_video_stop()` : Stop recording.


`Vilib.rec_video_set["path"] = f"/home/{username}/Videos/"` sets the storage location of video files.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.3.4 10. Bull Fight**


Make PiCar-X an angry bull! Use its camera to track and rush the red cloth!


**Run the Code**





**View the Image**


After the code runs, the terminal will display the following prompt:

```
No desktop !
* Serving Flask app "vilib.vilib" (lazy loading)
* Environment: production
WARNING: Do not use the development server in a production environment.
Use a production WSGI server instead.
* Debug mode: off
* Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

```

Then you can enter `http://<your IP>:9000/mjpg` in the browser to view the video screen. such as: `https://`
```
192.168.18.113:9000/mjpg

```

**2.3. 3. Computer Vision** **65**


**SunFounder PiCar-X Kit**


**Code**


**Note:** You can **Modify/Reset/Copy/Run/Stop** the code below. But before that, you need to go to source code path
like `picar-x\examples` . After modifying the code, you can run it directly to see the effect.



**66** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)







**How it works?**


You need to pay attention to the following three parts of this example:


1. Define the main function:


     - Start the camera using `Vilib.camera_start()` .


     - Display the camera feed using `Vilib.display()` .


     - Enable color detection and specify the target color as “red” using `Vilib.color_detect("red")` .


     - Initialize variables: `speed` for car movement speed, `dir_angle` for the direction angle of the car’s movement, `x_angle` for the camera’s pan angle, and `y_angle` for the camera’s tilt angle.


2. Enter a continuous loop (while True) to track the red-colored object:


     - Check if there is a detected red-colored object ( `Vilib.detect_obj_parameter['color_n'] != 0` ).


     - If a red-colored object is detected, obtain its coordinates ( `coordinate_x` and `coordinate_y` ).


     - Calculate new pan and tilt angles ( `x_angle` and `y_angle` ) based on the detected object’s position and
adjust them to track the object.


     - Limit the pan and tilt angles within the specified range using the `clamp_number` function.


     - Set the camera’s pan and tilt angles using `px.set_cam_pan_angle()` and `px.set_cam_tilt_angle()`
to keep the object in view.


3. Control the car’s movement based on the difference between dir_angle and `x_angle` :


     - If `dir_angle` is greater than `x_angle`, decrement `dir_angle` by 1 to gradually change the direction angle.


     - If `dir_angle` is less than `x_angle`, increment `dir_angle` by 1.


     - Set the direction servo angle using `px.set_dir_servo_angle()` to steer the car’s wheels accordingly.


     - Move the car forward at the specified speed using `px.forward(speed)` .


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


**2.3. 3. Computer Vision** **67**


**SunFounder PiCar-X Kit**


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.3.5 11. Video Car**


This program will provide a First Person View from the PiCar-X! Use the keyboards WSAD keys to control the direction
of movement, and the O and P to adjust the speed.


**Run the Code**





Once the code is running, you can see what PiCar-X is shooting and control it by pressing the following keys.


  - O: speed up


  - P: speed down


  - W: forward


  - S: backward


  - A: turn left


  - D: turn right


  - F: stop


  - T: take photo


  - Ctrl+C: quit


**View the Image**


After the code runs, the terminal will display the following prompt:

```
No desktop !
* Serving Flask app "vilib.vilib" (lazy loading)
* Environment: production
WARNING: Do not use the development server in a production environment.
Use a production WSGI server instead.
* Debug mode: off
* Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

```

Then you can enter `http://<your IP>:9000/mjpg` in the browser to view the video screen. such as: `https://`
```
192.168.18.113:9000/mjpg

```

**code**


**68** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**



**2.3. 3. Computer Vision** **69**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
      px.set_dir_servo_angle(-30)
      px.forward(speed)
    elif operate == 'turn right':
      px.set_dir_servo_angle(30)
      px.forward(speed)

def main():
  speed = 0
  status = 'stop'

  Vilib.camera_start(vflip=False,hflip=False)
  Vilib.display(local=True,web=True)
  sleep(2) # wait for startup
  print(manual)

  while True:
    print("\rstatus: %s, speed: %s "%(status, speed), end='', flush=True)
    # readkey
    key = readchar.readkey().lower()
    # operation
    if key in ('wsadfop'):
      # throttle
      if key == 'o':
        if speed <=90:
          speed += 10
      elif key == 'p':
        if speed >=10:
          speed -= 10
        if speed == 0:
          status = 'stop'
      # direction
      elif key in ('wsad'):
        if speed == 0:
           speed = 10
        if key == 'w':
           # Speed limit when reversing,avoid instantaneous current too large
           if status != 'forward' and speed > 60:
             speed = 60
           status = 'forward'
        elif key == 'a':
           status = 'turn left'
        elif key == 's':
           if status != 'backward' and speed > 60: # Speed limit when reversing
             speed = 60
           status = 'backward'
        elif key == 'd':
           status = 'turn right'
      # stop
      elif key == 'f':
        status = 'stop'

```

(continues on next page)


**70** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
      # move
      move(status, speed)
    # take photo
    elif key == 't':
      take_photo()
    # quit
    elif key == readchar.key.CTRL_C:
      print('\nquit ...')
      px.stop()
      Vilib.camera_close()
      break

    sleep(0.1)

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print("error: %s "%e)
  finally:
    px.stop()
    Vilib.camera_close()

```

**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**2.3.6 12. Controlled by the APP**


The SunFounder controller is used to control Raspberry Pi/Pico based robots.


The APP integrates Button, Switch, Joystick, D-pad, Slider and Throttle Slider widgets; Digital Display, Ultrasonic
Radar, Grayscale Detection and Speedometer input widgets.


There are 17 areas A-Q, where you can place different widgets to customize your own controller.


In addition, this application provides a live video streaming service.


Let’s customize a PiCar-X controller using this app.


**How to do?**


**2.3. 3. Computer Vision** **71**


**SunFounder PiCar-X Kit**


1. Install the `sunfounder-controller` module.


The `robot-hat`, `vilib`, and `picar-x` modules need to be installed first, for details see: _Install All_
_the Modules (Important)_ .





2. Run the code.





[3. Install SunFounder Controller from](https://docs.sunfounder.com/projects/sf-controller/en/latest/) **APP Store(iOS)** or **Google Play(Android)** .


4. Open and create a new controller.


Create a new controller by clicking on the + sign in the SunFounder Controller APP.


There are preset controllers for some products in the Preset section, which you can use as needed.
Here, we select **PiCar-X** .


**72** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


5. Connect to PiCar-x.


When you click the **Connect** button, it will automatically search for robots nearby. Its name is defined
in `picarx_control.py` and it must be running at all times.


Once you click on the product name, the message “Connected Successfully” will appear and the
product name will appear in the upper right corner.


**2.3. 3. Computer Vision** **73**


**SunFounder PiCar-X Kit**


**Note:**


       - You need to make sure that your mobile device is connected to the same LAN as PiCar-X.


        - If it doesn’t search automatically, you can also manually enter the IP to connect.


6. Run this controller.


Click the **Run** button to start the controller, you will see the footage of the car shooting, and now you
can control your PiCar-X with these widgets.


**74** **Chapter 2. Play with Python**


**SunFounder PiCar-X Kit**


Here are the functions of the widgets.


        - **A** : Show the current speed of the car.


        - **E** : turn on the obstacle avoidance function.


        - **I** : turn on the line following function.


        - **J** : voice recognition, press and hold this widget to start speaking, and it will show the recognized
voice when you release it. We have set `forward`, `backard`, `left` and `right` 4 commands in the
code to control the car.


        - **K** : Control forward, backward, left, and right motions of the car.


        - **Q** : turn the head(Camera) up, down, left and right.


        - **N** : Turn on the color recognition function.


        - **O** : Turn on the face recognition function.


        - **P** : Turn on the object recognition function, it can recognize nearly 90 kinds of objects, for the list
[of models, please refer to: https://github.com/sunfounder/vilib/blob/master/workspace/coco_](https://github.com/sunfounder/vilib/blob/master/workspace/coco_labels.txt)
[labels.txt.](https://github.com/sunfounder/vilib/blob/master/workspace/coco_labels.txt)


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


**2.3. 3. Computer Vision** **75**


**SunFounder PiCar-X Kit**


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**76** **Chapter 2. Play with Python**


**CHAPTER**
