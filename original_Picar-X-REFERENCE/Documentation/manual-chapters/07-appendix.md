### **SEVEN** **APPENDIX**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **7.1 I [2] C Configuration**


Follow the steps below to enable and test the I [2] C interface on your Raspberry Pi. These instructions apply to Raspberry
Pi 5, 4, 3, and Zero 2W.


**7.1.1 Enable the I** **[2]** **C Interface**


1. Open a terminal on your computer (Windows: **PowerShell** ; macOS/Linux: **Terminal** ) and connect to your
Raspberry Pi:

```
   ssh <username>@<hostname>.local

```

or:

```
   ssh <username>@<ip_address>

```

2. Open the Raspberry Pi configuration tool:

```
   sudo raspi-config

```

3. Select **Interfacing Options** and press **Enter** .


**221**


**SunFounder PiCar-X Kit**


4. Select **I2C** .


5. Choose **<Yes>**, then **<Ok>** _→_ **<Finish>** to apply the changes. If prompted, reboot your Raspberry Pi.


**222** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**



**7.1.2 Check I** **[2]** **C Kernel Modules**


1. Run the following command:

```
   lsmod | grep i2c

```

2. If I [2] C is enabled, you will see modules such as:





3. If nothing appears, reboot the system:

```
   sudo reboot

```

**7.1.3 Install i2c-tools**


1. Install the utilities required for scanning and testing I [2] C devices:

```
   sudo apt install i2c-tools

```

**7.1. I** **[2]** **C Configuration** **223**


**SunFounder PiCar-X Kit**


**7.1.4 Detect Connected I** **[2]** **C Devices**


1. Scan the I [2] C bus:

```
   i2cdetect -y 1

```

2. Example output:

```
   pi@raspberrypi ~ $ i2cdetect -y 1
     0 1 2 3 4 5 6 7 8 9 a b c d e f
   00: -- -- -- -- -- -- -- -- -- -- -- -- -   10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -   20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -   30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -   40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- -   50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -   60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -   70: -- -- -- -- -- -- -- -
```

3. If a device is connected, its address (e.g., **0x48** ) will appear in the table.


**7.1.5 Install the Python I** **[2]** **C Library**


1. Install the `python3-smbus2` package:

```
   sudo apt install python3-smbus2

```

The `smbus2` library provides all the functions required to communicate with I [2] C devices in Python.


Your Raspberry Pi is now fully configured and ready to communicate with I [2] C devices.


**Note:** Hello, welcome to the SunFounder Raspberry Pi, Arduino, and ESP32 Enthusiasts Community on Facebook!
Join fellow makers to explore, learn, and create together.


**Why Join?**


   - **Expert Support**   - Get help with post-sale issues and technical challenges.


   - **Learn & Share**   - Exchange tutorials, tips, and hands-on experiences.


   - **Exclusive Previews**   - Get early access to new product announcements.


   - **Special Discounts**   - Enjoy members-only offers on new products.


   - **Giveaways & Events**   - Join festive promotions and prize draws.


Click to join the community!


**224** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**

### **7.2 SPI Configuration**


Follow the steps below to enable and verify the SPI interface on your Raspberry Pi. These instructions apply to Raspberry Pi 5, 4, 3, and Zero 2W.


**7.2.1 Enable the SPI Interface**


1. Open a terminal on your computer (Windows: **PowerShell** ; macOS/Linux: **Terminal** ) and connect to your
Raspberry Pi:

```
   ssh <username>@<hostname>.local

```

or:

```
   ssh <username>@<ip_address>

```

2. Open the Raspberry Pi configuration tool:

```
   sudo raspi-config

```

3. Select **Interfacing Options** and press **Enter** .


4. Select **SPI** .


**7.2. SPI Configuration** **225**


**SunFounder PiCar-X Kit**


5. Choose **<Yes>**, then **<Ok>** _→_ **<Finish>** to apply the changes. If prompted, reboot your Raspberry Pi.


**226** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**



**7.2.2 Verify SPI Interface**


1. Check whether the SPI device nodes exist:

```
   ls /dev/sp*

```

2. If the SPI interface is enabled, the output will include:






     - If these devices appear, SPI is active and ready to use.


     - If not, reboot your Raspberry Pi and check again.


**7.2.3 Install spidev (Python SPI Library)**


1. Install the `spidev` package to use SPI in Python:

```
   sudo apt install python3-spidev

```

The `spidev` library provides access to SPI devices through the `/dev/spidevX.Y` interface.


Your Raspberry Pi is now configured to communicate with SPI devices using both command-line tools and Python.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **7.3 Remote Desktop**


You can access and control the Raspberry Pi desktop remotely from another computer. The recommended method is
**VNC**, which is officially supported on Raspberry Pi OS and provides a reliable and consistent desktop experience.


The following section explains how to enable VNC on your Raspberry Pi and connect to it using .


**7.3. Remote Desktop** **227**


**SunFounder PiCar-X Kit**


**7.3.1 Enable the VNC Service**


RealVNC Server is preinstalled on Raspberry Pi OS, but it is **disabled by default** . You must enable it through the
configuration tool.


1. Open a terminal on your computer (Windows: **PowerShell** ; macOS/Linux: **Terminal** ) and connect to your
Raspberry Pi:

```
   ssh <username>@<hostname>.local

```

or

```
   ssh <username>@<ip_address>

```

2. Run the configuration tool:

```
   sudo raspi-config

```

3. Select **Interfacing Options** and press **Enter** .


**228** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


4. Select **VNC** .


5. Choose **Yes**, then **OK**, and finally **Finish** to exit.


**7.3. Remote Desktop** **229**


**SunFounder PiCar-X Kit**


**7.3.2 Log in with RealVNC® Viewer**


1. Download and install for your operating system.


2. Open **RealVNC Viewer**, then enter your Raspberry Pi’s IP address or `<hostname>.local` and press **Enter** .


**230** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


3. Enter your Raspberry Pi’s **username** and **password**, then select **OK** .


**Note:** When connecting for the first time, you may see a message such as “VNC Server not recognized”. Select
**Continue** to proceed.


**7.3. Remote Desktop** **231**


**SunFounder PiCar-X Kit**


4. You should now see the Raspberry Pi desktop:


**232** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


This completes the VNC setup process.


**7.3.3 Additional Notes**


   - **Desktop version required**


**–** VNC requires the Raspberry Pi to be running the full desktop version of Raspberry Pi OS.


**–** If you are using **Raspberry Pi OS Lite**, install VNC Server manually: `sudo apt install`
```
     realvnc-vnc-server

```

   - **Network performance tips**


**–** If you experience lag or slow refresh rates, check your network quality.


**–** Wired Ethernet generally offers the best performance.


   - **Fixing display resolution issues**


**–** If the VNC window appears too small or the resolution is incorrect, set a fixed resolution via: `sudo`
`raspi-config` _→_ **Display Options** _→_ **VNC Resolution**


   - **Ensure VNC is enabled**


If VNC fails to connect, verify that it is enabled in: `sudo raspi-config` _→_ `Interfacing Options` _→_ `VNC`


**7.3. Remote Desktop** **233**


**SunFounder PiCar-X Kit**


   - **Stopping the VNC service**


To manually stop the VNC Server: `sudo systemctl stop vncserver-x11-serviced`


   - **Security reminder**


**–** VNC is designed for trusted local networks.


**–** Do **not** expose VNC directly to the internet.


**–** For secure remote access from outside your network, use **Raspberry Pi Connect** or a VPN.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **7.4 FileZilla Software**


File Transfer Protocol (FTP) is commonly used to transfer files between computers over a network. **FileZilla** is an
open-source client that supports FTP, FTPS, and **SFTP** (recommended for Raspberry Pi). With FileZilla, you can
easily upload files (such as images, audio, and scripts) from your computer to the Raspberry Pi, or download files from
the Pi back to your computer.


**7.4.1 Download FileZilla**


1. Visit the official website and download **FileZilla Client** for your operating system.


2. Install and launch the program.


**234** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


3. Open FileZilla and enter the following information:


      - **Host:** `<hostname>.local` or the Raspberry Pi’s IP address


      - **Username:** your Pi username


      - **Password:** the password set in Raspberry Pi Imager


      - **Port:** `22` (for SFTP)


     - Click **Quickconnect** (or press **Enter** ) to establish a connection.


4. Once connected, the left panel shows your **local files**, and the right panel shows the **Raspberry Pi files** .


**7.4. FileZilla Software** **235**


**SunFounder PiCar-X Kit**


5. You can:


      - **Upload** a file: drag from the left panel _→_ right panel


      - **Download** a file: drag from the right panel _→_ left panel


FileZilla will immediately start the transfer, and the status will appear in the panel at the bottom.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**236** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**

### **7.5 Install OpenSSH via PowerShell**


If you see the following error when running `ssh <username>@<hostname>.local` or `ssh <username>@<IP>` :



It means your Windows system does not have OpenSSH installed. Follow the steps below to install it manually.


1. Open the Windows Start Menu, type **powershell**, right-click **Windows PowerShell**, and select **Run as admin-**
**istrator** .


2. Install the OpenSSH Client:

```
   Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

```

3. After installation, you should see output similar to:





4. Verify the installation:

```
 Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'

```

5. If OpenSSH is installed, the output will include:





**Warning:** If `Installed` does not appear, your Windows system may be too old. In this case, we recommend
using a third-party SSH tool. See: _PuTTY_


6. Close PowerShell, reopen it (no need to run as administrator this time), and use the `ssh` command to log in:

```
   ssh <username>@<hostname>.local

```

**7.5. Install OpenSSH via PowerShell** **237**


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

### **7.6 PuTTY**


PuTTY is a simple and reliable SSH client for Windows users to remotely access the Raspberry Pi.


1. Download PuTTY from and install it on your computer.


**238** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


2. Open PuTTY and prepare the connection:


     - Enter your Raspberry Pi’s **hostname or IP address** in **Host Name** .


     - Set the **Port** to `22` .


     - Click **Open** to connect.


3. If a security warning appears on first use, click **Accept** to continue.


**7.6. PuTTY** **239**


**SunFounder PiCar-X Kit**


4. Log in to the Raspberry Pi:


    - When you see **login as:**, enter the username you set in **Raspberry Pi Imager** .


     - Enter your password (it will not appear while typing—this is normal).


     - After logging in, the terminal is ready for you to enter commands and operate your Raspberry Pi remotely.


**Note:** If PuTTY shows **inactive**, the connection was lost and needs to be reconnected.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


**240** **Chapter 7. Appendix**


**SunFounder PiCar-X Kit**


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**7.6. PuTTY** **241**


**SunFounder PiCar-X Kit**


**242** **Chapter 7. Appendix**


**CHAPTER**
