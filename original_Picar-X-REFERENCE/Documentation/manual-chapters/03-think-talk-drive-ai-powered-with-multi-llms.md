### **THREE** **THINK · TALK · DRIVE — AI-POWERED WITH MULTI-LLMS**


Go beyond movement and vision by adding **speech** and **AI** . Here you will explore text-to-speech (TTS), speech-to-text
(STT), and large language models (LLMs) to make your PiCar-X talk, listen, and even chat with you like a smart robot.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **3.1 13. Play Music and Sound Effects**


In this project, you will learn how to make the PiCar-X play background music or sound effects. You can also play
music files that you have stored.


**Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**Run the Code**





After the code runs, please operate according to the prompt that printed on the terminal.


Input key to call the function!


  - space: Play sound effect (Car horn)


  - c: Play sound effect with threads


  - q: Play/Stop Music



**77**


**SunFounder PiCar-X Kit**


**Code**



**How it works?**


Functions related to background music include these:


   - `music = Music()` : Declare the object.


   - `music.music_set_volume(20)` : Set the volume, the range is 0~100.


   - `music.music_play('../musics/slow-trail-Ahjay_Stelino.mp3')` : Play music files, here is the **slow-**
**trail-Ahjay_Stelino.mp3** file under the `../musics` path.


   - `music.music_stop()` : Stop playing background music.


**78** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**Note:** You can add different sound effects or music to `musics` or `sounds` folder via _FileZilla Software_ .


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **3.2 14. Voice Prompt Car with Espeak and Pico2Wave**


In this lesson, we’ll use two built-in text-to-speech (TTS) engines on Raspberry Pi — **Espeak** and **Pico2Wave** - to
make the PiCar-X talk.


These two engines are both simple and run offline, but they sound quite different:


   - **Espeak** : very lightweight and fast, but the voice is robotic. You can adjust speed, pitch, and volume.


   - **Pico2Wave** : produces a smoother and more natural voice than Espeak, but has fewer options to configure.


You’ll hear the difference in **voice quality** and **features**, and then build a “voice prompt car” that announces its actions
before moving.


**3.2.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.2.2 1. Testing Espeak**


Espeak is a lightweight TTS engine included in Raspberry Pi OS. Its voice sounds robotic, but it is highly configurable:
you can adjust volume, pitch, speed, and more.


**Steps to try it out** :


  - Create a new file with the command:






  - Then copy the example code into it. Press `Ctrl+X`, then `Y`, and finally `Enter` to save and exit.


**3.2. 14. Voice Prompt Car with Espeak and Pico2Wave** **79**


**SunFounder PiCar-X Kit**




  - Run the program with:

```
   sudo python3 test_tts_espeak.py

```

  - You should hear the PiCar-X say: “Hello! I’m Espeak TTS.”


  - Uncomment the voice tuning lines in the code to experiment with how `amp`, `speed`, `gap`, and `pitch` affect the
sound.


**3.2.3 2. Testing Pico2Wave**


Pico2Wave produces a more natural, human-like voice than Espeak. It’s simpler to use but less flexible — you can only
change the language, not the pitch or speed.


**Steps to try it out** :


  - Create a new file with the command:






  - Then copy the example code into it. Press `Ctrl+X`, then `Y`, and finally `Enter` to save and exit.

```
   from picarx.tts import Pico2Wave

   tts = Pico2Wave()

   tts.set_lang('en-US') # en-US, en-GB, de-DE, es-ES, fr-FR, it-IT

   # Quick hello (sanity check)
   tts.say("Hello! I'm Pico2Wave TTS.")

```

  - Run the program with:

```
   sudo python3 test_tts_pico2wave.py

```

  - You should hear the PiCar-X say: “Hello! I’m Pico2Wave TTS.”


  - Try switching the language (for example, `es-ES` for Spanish) and listen to the difference.


**80** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**3.2.4 3. Voice Prompt Car**


Now let’s combine **Pico2Wave** or **Espeak** with PiCar-X driving code to create a “voice prompt car”: before every
action, the car will announce what it’s about to do.


**Run the Code**





Run this code and you’ll see your PiCar-X drive forward, backward, and turn, each time announcing its move first. This
makes your car safer, friendlier, and more interactive.


**Code**



**3.2. 14. Voice Prompt Car with Espeak and Pico2Wave** **81**


**SunFounder PiCar-X Kit**


(continued from previous page)



**3.2.5 Troubleshooting**


   - **No sound when running Espeak or Pico2Wave**


**–** Check that your speakers/headphones are connected and volume is not muted.


**–** Run a quick test in terminal:





If you hear nothing, the issue is with audio output, not your Python code.


- **Espeak voice sounds too fast or too robotic**


**–** Try adjusting the parameters in your code:






   - **Permission denied when running code**


**–** Try running with `sudo` :

```
     sudo python3 test_tts_espeak.py

```

**3.2.6 Comparison: Espeak vs Pico2Wave**


**82** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


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

### **3.3 15. AI Storytelling Robot with Piper and OpenAI**


In the previous lesson, we tried two built-in TTS engines on Raspberry Pi ( **Espeak** and **Pico2Wave** ). Now let’s explore
two more powerful options: **Piper** (offline, neural network-based) and **OpenAI TTS** (online, cloud-based).


   - **Piper** : a local TTS engine that runs offline on Raspberry Pi.


   - **OpenAI TTS** : an online service that provides very natural, human-like voices.


At the end, your PiCar-X will drive around and tell jokes like a little storyteller.


**3.3.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.3.2 1. Testing Piper**


**Steps to try it out** :


1. Create a new file:





2. Copy the example code below into the file. Press `Ctrl+X`, then `Y`, and finally `Enter` to save and exit.

```
   from picarx.tts import Piper

   tts = Piper()

   # List supported languages
```

(continues on next page)


**3.3. 15. AI Storytelling Robot with Piper and OpenAI** **83**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
   print(tts.available_countrys())

   # List models for English (en_us)
   print(tts.available_models('en_us'))

   # Set a voice model (auto-download if not already present)
   tts.set_model("en_US-amy-low")

   # Say something
   tts.say("Hello! I'm Piper TTS.")

```

      - `available_countrys()` : print supported languages.


      - `available_models()` : list available models for that language.


      - `set_model()` : set the voice model (downloads automatically if missing).


      - `say()` : convert text to speech and play it.


3. Run the program:

```
   sudo python3 test_tts_piper.py

```

4. The first time you run it, the selected voice model will be downloaded automatically.


     - You should then hear the PiCar-X say: `Hello! I'm Piper TTS.`


     - You can change to another language model by calling `set_model()` with a different name.


**3.3.3 2. Testing OpenAI TTS**


**Get and save your API Key**


1. Go to and log in. On the **API keys** page, click **Create new secret key** .


**84** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


2. Fill in the details (Owner, Name, Project, and permissions if needed), then click **Create secret key** .


**3.3. 15. AI Storytelling Robot with Piper and OpenAI** **85**


**SunFounder PiCar-X Kit**


3. Once the key is created, copy it right away — you won’t be able to see it again. If you lose it, you must generate
a new one.


**86** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


4. In your project folder (for example: `/picar-x/example` ), create a file called `secret.py` :





5. Paste your key into the file like this:





**Write and Run a Test Program**


1. Create a new file:





2. Copy the example code below into the file. Press `Ctrl+X`, then `Y`, and finally `Enter` to save and exit.

```
   from picarx.tts import OpenAI_TTS
   from secret import OPENAI_API_KEY # or use the try/except version shown above

   # Initialize OpenAI TTS
   tts = OpenAI_TTS(api_key=OPENAI_API_KEY)
   tts.set_model('gpt-4o-mini-tts') # low-latency TTS model
   tts.set_voice('alloy') # pick a voice

   # Quick hello (sanity check)
   tts.say("Hello! I'm OpenAI TTS.")

```

**3.3. 15. AI Storytelling Robot with Piper and OpenAI** **87**


**SunFounder PiCar-X Kit**


3. Run the program:

```
   sudo python3 test_tts_openai.py

```

4. You should hear the PiCar-X say:

```
   Hello! I'm OpenAI TTS.

```

**3.3.4 3. Storytelling Robot**


Now that we have tested both **Piper** and **OpenAI TTS**, let’s use them in a real project: a **storytelling robot car** that
drives around while telling jokes.


In this program, the PiCar-X will:


  - Greet you with TTS when it starts.


  - Move forward and tell a first joke.


  - Move forward again and tell a second joke.


  - Finally drive backward, return “home,” and say goodbye.


It’s like having a little robot storyteller on wheels!


**Run the code**





**Code**

```
from picarx import Picarx
import time

# === TTS Configuration ===
# Default: Piper
from picarx.tts import Piper
tts = Piper()
tts.set_model("en_US-amy-low") # use the voice model you installed

# Optional: switch to OpenAI TTS
# from picarx.tts import OpenAI_TTS
# from secret import OPENAI_API_KEY
# tts = OpenAI_TTS(api_key=OPENAI_API_KEY)
# tts.set_model("gpt-4o-mini-tts") # low-latency TTS model
# tts.set_voice("alloy") # choose a voice

# === PiCar-X Setup ===
px = Picarx()

# Quick hello (sanity check)
tts.say("Hello! I'm PiCar-X speaking with Piper.")

def main():
  try:
    # Leg 1
```

(continues on next page)


**88** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
    px.forward(30)
    time.sleep(3)
    px.stop()
    tts.say("Why can't your nose be twelve inches long? Because then it would be a␣
```

_˓→_ `foot!")`

```
    # Leg 2
    px.forward(30)
    time.sleep(3)
    px.stop()
    tts.say("Why did the cow go to outer space? To see the moooon!")

    # Wrap-up
    tts.say("That's all for today. Goodbye, let's go home and sleep.")
    px.backward(30)
    time.sleep(6)
    px.stop()

  except KeyboardInterrupt:
    px.stop()
  finally:
    px.stop()
    px.set_dir_servo_angle(0)

if __name__ == "__main__":
  main()

```

**3.3.5 Troubleshooting**


   - **No module named ‘secret’**


This means `secret.py` is not in the same folder as your Python file. Move `secret.py` into the same directory
where you run the script, e.g.:






   - **OpenAI: Invalid API key / 401**


**–** Check that you pasted the full key (starts with `sk-` ) and there are no extra spaces/newlines.


**–** Ensure your code imports it correctly:

```
     from secret import OPENAI_API_KEY

```

**–** Confirm network access on your Pi (try `ping api.openai.com` ).


   - **OpenAI: Quota exceeded / billing error**


**–** You may need to add billing or increase quota in the OpenAI dashboard.


**–** Try again after resolving the account/billing issue.


   - **Piper: tts.say() runs but no sound**


**3.3. 15. AI Storytelling Robot with Piper and OpenAI** **89**


**SunFounder PiCar-X Kit**


**–** Make sure a voice model is actually present:

```
     ls ~/.local/share/piper/voices

```

**–** Confirm your model name matches exactly in code:

```
     tts.set_model("en_US-amy-low")

```

**–** Check the audio output device/volume on your Pi ( `alsamixer` ), and that speakers are connected and powered.


   - **ALSA / sound device errors (e.g., “Audio device busy” or “No such file or directory”)**


**–** Close other programs using audio.


**–** Reboot the Pi if the device stays busy.


**–** For HDMI vs. headphone jack output, select the correct device in Raspberry Pi OS audio settings.


   - **Permission denied when running Python**


**–** Try with `sudo` if your environment requires it:

```
     sudo python3 test_tts_piper.py

```

**3.3.6 Comparison of TTS Engines**


Table 1: Feature comparison: Espeak vs Pico2Wave vs Piper vs OpenAI
TTS

































**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


**90** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **3.4 16. Voice Controlled Car with Vosk (Offline)**


Vosk is a lightweight speech-to-text (STT) engine that supports many languages and runs fully **offline** on Raspberry
Pi. You only need internet access once to download a language model. After that, everything works without a network
connection.


In this lesson, we will:


  - Check the microphone on Raspberry Pi.


  - Install and test Vosk with a chosen language model.


  - Build a **voice controlled PiCar-X** that listens for a wake word and then responds to commands like **forward**,
**backward**, **left**, and **right** .


**3.4.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.4.2 1. Check Your Microphone**


Before using speech recognition, make sure your USB microphone works correctly.


1. List available recording devices:

```
   arecord -l

```

Look for a line like `card 1:` `...` `device 0` .


2. Record a short sample (replace `1,0` with the numbers you found):

```
   arecord -D plughw:1,0 -f S16_LE -r 16000 -d 3 test.wav

```

     - Example: if your device is `card 2, device 0`, use:

```
   arecord -D plughw:2,0 -f S16_LE -r 16000 -d 3 test.wav

```

3. Play it back to confirm the recording:

```
   aplay test.wav

```

4. Adjust microphone volume if needed:


**3.4. 16. Voice Controlled Car with Vosk (Offline)** **91**


**SunFounder PiCar-X Kit**

```
   alsamixer

```

     - Press **F6** to select your USB microphone.


     - Find the **Mic** or **Capture** channel.


     - Make sure it is not muted ( **[MM]** means mute, press `M` to unmute _→_ should show **[OO]** ).


     - Use ↑/ ↓arrow keys to change the recording volume.


**3.4.3 2. Test Vosk**


**Steps to try it out** :


1. Create a new file:





2. Copy the example code into it. Press `Ctrl+X`, then `Y`, and `Enter` to save and exit.

```
 from picarx.stt import Vosk

 vosk = Vosk(language="en-us")

 print(vosk.available_languages)

 while True:
   print("Say something")
   result = vosk.listen(stream=False)
   print(result)

```

3. Run the program:

```
 sudo python3 test_stt_vosk.py

```

4. The first time you run this code with a new language, Vosk will **automatically download the language model**
(by default it will download the **small** version). At the same time, it will also print out the list of supported
languages. Then you will see:



This means:


     - The model file ( `vosk-model-small-en-us-0.15` ) has been downloaded.


     - The list of supported languages has been printed.


     - The system is now listening — say something into the PiCar-X microphone, and the recognized text will
appear in the terminal.


**Tips** :


     - Keep the microphone about 15–30 cm away.


**92** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**




     - Pick a model that matches your language and accent.


**Streaming Mode (optional)**


You can also stream speech continuously to see partial results as you speak:





**3.4.4 3. Voice Controlled Car**


Now let’s connect speech recognition to the PiCar-X!


We will use a **wake word** (“hey robot”) so the car only listens for commands after being activated. This saves CPU
and prevents unwanted triggers.


**Run the code**





In this program, the car:


  - Waits for the wake word **“hey robot”** .


  - After that, you can speak naturally — as long as your sentence includes one of the keywords ( **forward**, **backward**,
**left**, **right** ), the car will respond.


For example:


**–** “Can you move forward a little?” _→_ the car moves forward.


**–** “Please turn left now.” _→_ the car turns left.


  - The command **“sleep”** stops the control loop and puts the car back into waiting mode.


**Code**







**3.4. 16. Voice Controlled Car with Vosk (Offline)** **93**


**SunFounder PiCar-X Kit**

```
try:
  while True:

```


(continued from previous page)


```
    # --- wait for wake word once --    stt.wait_until_heard(WAKE_WORDS)
    print("Wake word detected. Listening for commands... (say 'sleep' to pause)")

    # --- command loop: multiple commands after one wake --    while True:
      res = stt.listen(stream=False)
      text = res.get("text", "") if isinstance(res, dict) else str(res)
      text = text.lower().strip()
      if not text:
        continue

      print("Heard:", text)

      if "sleep" in text:
        # pause command mode; go back to wait for wake word
        px.stop(); px.set_dir_servo_angle(0)
        print("Sleeping. Say 'hey robot' to wake me again.")
        break

      elif "forward" in text:
        px.set_dir_servo_angle(0)
        px.forward(30); time.sleep(1); px.stop()

      elif "backward" in text:
        px.set_dir_servo_angle(0)
        px.backward(30); time.sleep(1); px.stop()

      elif "left" in text:
        px.set_dir_servo_angle(-25)
        px.forward(30); time.sleep(1)
        px.stop(); px.set_dir_servo_angle(0)

      elif "right" in text:
        px.set_dir_servo_angle(25)
        px.forward(30); time.sleep(1)
        px.stop(); px.set_dir_servo_angle(0)
      # (ignore other words)

except KeyboardInterrupt:
  pass
finally:
  px.stop(); px.set_dir_servo_angle(0)
  print("Stopped and centered. Bye.")

```

**94** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**3.4.5 Troubleshooting**


   - **No such file or directory (when running `arecord`)**


You may have used the wrong card/device number. Run:

```
   arecord -l

```

and replace `1,0` with the numbers shown for your USB microphone.


   - **Recorded file has no sound**


Open the mixer and check the microphone volume:

```
   alsamixer

```

**–** Press **F6** to select your USB mic.


**–** Make sure **Mic/Capture** is not muted ( **[OO]** instead of **[MM]** ).


**–** Increase the level with ↑.


   - **Vosk does not recognize speech**


**–** Make sure the **language code** matches your model (e.g. `en-us` for English, `zh-cn` for Chinese).


**–** Keep the microphone 15–30 cm away and avoid background noise.


**–** Speak clearly and slowly.


   - **Wake word (“hey robot”) never triggers**


**–** Say it in a natural tone, not too fast.


**–** Check that the program prints recognized text at all. If not, the microphone is not working.


   - **High latency / slow recognition**


**–** The default auto-download is a **small model** (faster, but less accurate).


**–** If it’s still slow, close other programs to free CPU.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**3.4. 16. Voice Controlled Car with Vosk (Offline)** **95**


**SunFounder PiCar-X Kit**

### **3.5 17. Text Vision Talk with Ollama**


In this lesson, you will learn how to use **Ollama**, a tool for running large language and vision models locally. We will
show you how to install Ollama, download a model, and connect PiCar-X to it.


With this setup, PiCar-X can take a camera snapshot and the model will **see and tell** - you can ask any question about
the image, and the model will reply in natural language.


**3.5.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.5.2 1. Install Ollama (LLM) and Download Model**


You can choose where to install **Ollama** :


  - On your Raspberry Pi (local run)


  - Or on another computer (Mac/Windows/Linux) in the **same local network**


**Recommended models vs hardware**


You can choose any model available on . Models come in different sizes (3B, 7B, 13B, 70B...). Smaller models run
faster and require less memory, while larger models provide better quality but need powerful hardware.


Check the table below to decide which model size fits your device.


**Install on Raspberry Pi**


If you want to run Ollama directly on your Raspberry Pi:


  - Use a **64-bit Raspberry Pi OS**


  - Strongly recommended: **Raspberry Pi 5 (16GB RAM)**


Run the following commands:

```
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a lightweight model (good for testing)
ollama pull llama3.2:3b

```

_`# Quick run test (type`_ _'_ _`hi`_ _'_ _`and press Enter)`_
```
ollama run llama3.2:3b
```

(continues on next page)


**96** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
# Serve the API (default port 11434)
# Tip: set OLLAMA_HOST=0.0.0.0 to allow access from LAN
OLLAMA_HOST=0.0.0.0 ollama serve

```

**Install on Mac / Windows / Linux (Desktop App)**


1. Download and install Ollama from


2. Open the Ollama app, go to the **Model Selector**, and use the search bar to find a model. For example, type
`llama3.2:3b` (a small and lightweight model to start with).


**3.5. 17. Text Vision Talk with Ollama** **97**


**SunFounder PiCar-X Kit**


3. After the download is complete, type something simple like “Hi” in the chat window, Ollama will automatically
start downloading it when you first use it.


4. Go to **Settings** _→_ enable **Expose Ollama to the network** . This allows your Raspberry Pi to connect to it over
LAN.


**98** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**Warning:** If you see an error like:

```
 Error: model requires more system memory ...

```

The model is too large for your machine. Use a **smaller model** or switch to a computer with more RAM.


**3.5.3 2. Test Ollama**


Once Ollama is installed and your model is ready, you can quickly test it with a minimal chat loop.


**Steps**


1. Create a new file:





2. Paste the following code and save ( `Ctrl+X` _→_ `Y` _→_ `Enter` ):

```
   from picarx.llm import Ollama

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   # If Ollama runs on the same Raspberry Pi, use "localhost".
```

_`# If it runs on another computer in your LAN, replace with that computer`_ _'_ _`s IP`_ `␣`

(continues on next page)


**3.5. 17. Text Vision Talk with Ollama** **99**


**SunFounder PiCar-X Kit**


_˓→_ _`address.`_
```
   llm = Ollama(
     ip="localhost",
     model="llama3.2:3b" # you can replace with any model
   )

   # Basic configuration
   llm.set_max_messages(20)
   llm.set_instructions(INSTRUCTIONS)
   llm.set_welcome(WELCOME)

   print(WELCOME)

   while True:
     text = input(">>> ")
     if text.strip().lower() in {"exit", "quit"}:
       break

     # Response with streaming output
     response = llm.prompt(text, stream=True)
     for token in response:
       if token:
         print(token, end="", flush=True)
     print("")

```

3. Run the program:

```
   python3 test_llm_ollama.py

```

4. Now you can chat with PiCar-X directly from the terminal.



(continued from previous page)




    - You can choose **any model** available on, but smaller models (e.g. `moondream:1.8b`, `phi3:mini` ) are
recommended if you only have 8–16GB RAM.


     - Make sure the model you specify in the code matches the model you have already pulled in Ollama.


    - Type `exit` or `quit` to stop the program.


     - If you cannot connect, ensure that Ollama is running and that both devices are on the same LAN if you are
using a remote host.


**3.5.4 3. Vision Talk with Ollama**


In this demo, the Pi camera takes a snapshot **each time you type a question** . The program sends **your typed text + the**
**new photo** to a local vision model via Ollama, and then streams the model’s reply in plain English. This is a minimal
“see & tell” baseline you can later extend with color/face/QR checks.


**Before You Start**


1. Open the **Ollama** app (or run the service) and make sure a **vision-capable model** is pulled.


    - If you have enough memory (16GB RAM), you may try `llava:7b` .


    - If you only have **8GB RAM**, prefer a smaller model such as `moondream:1.8b` or `granite3.`
`2-vision:2b` .


**100** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**



**Run the Demo**


1. Go to the example folder and run the script:





2. What happens when it runs:


     - The program prints a welcome line and waits for your input ( `>>>` ).


      - **Every time you type anything** (e.g., “hello”, “Is there yellow?”, “Any faces?”, “What is on the desk?”), it:


**– captures a photo** from the Pi camera (saved to `/tmp/llm-img.jpg` ),


**– sends your text + the photo** to the vision model via Ollama,


**– streams back** the model’s answer to the terminal.


    - Type `exit` or `quit` to end the program.


**Code**

```
from picarx.llm import Ollama
from picamera2 import Picamera2
import time

"""
You need to set up Ollama first.
```

(continues on next page)


**3.5. 17. Text Vision Talk with Ollama** **101**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
Note: At least 8GB RAM is recommended for small vision models (e.g., moondream:1.8b).
   For llava:7b, more memory is preferred (16GB).
"""

INSTRUCTIONS = "You are a helpful assistant."
WELCOME = "Hello, I am a helpful assistant. How can I help you?"

# If Ollama runs on the same Pi, use "localhost".
```

_`# If it runs on another computer in your LAN, replace with that computer`_ _'_ _`s IP.`_
```
llm = Ollama(
  ip="localhost", # e.g., "192.168.100.145" if remote
  model="llava:7b" # change to "moondream:1.8b" or "granite3.2-vision:2b" for ␣
```

_˓→_ _`8GB RAM`_
```
)

# Basic configuration
llm.set_max_messages(20)
llm.set_instructions(INSTRUCTIONS)
llm.set_welcome(WELCOME)

# Init camera
camera = Picamera2()
config = camera.create_still_configuration(
  main={"size": (1280, 720)},
)
camera.configure(config)
camera.start()
time.sleep(2)

print(WELCOME)

while True:
  input_text = input(">>> ")
  if input_text.strip().lower() in {"exit", "quit"}:
    break

  # Capture image
  img_path = "/tmp/llm-img.jpg"
  camera.capture_file(img_path)

  # Response with stream (text + image)
  response = llm.prompt(input_text, stream=True, image_path=img_path)
  for next_word in response:
    if next_word:
      print(next_word, end="", flush=True)
  print("")

```

**102** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**3.5.5 Troubleshooting**


   - **I get an error like: `model requires more system memory ...`.**


**–** This means the model is too large for your device.


**–** Use a smaller model such as `moondream:1.8b` or `granite3.2-vision:2b` .


**–** Or switch to a machine with more RAM and expose Ollama to the network.


   - **The code cannot connect to Ollama (connection refused).**


Check the following:


**–** Make sure Ollama is running ( `ollama serve` or the desktop app is open).


**–** If using a remote computer, enable **Expose to network** in Ollama settings.


**–** Double-check that the `ip="..."` in your code matches the correct LAN IP.


**–** Confirm both devices are on the same local network.


   - **My Pi camera does not capture anything.**


**–** Verify that `Picamera2` is installed and working with a simple test script.


**–** Check that the camera cable is properly connected and enabled in `raspi-config` .


**–** Ensure your script has permission to write to the target path ( `/tmp/llm-img.jpg` ).


   - **The output is too slow.**


**–** Smaller models reply faster, but with simpler answers.


**–** You can lower the camera resolution (e.g., 640×480 instead of 1280×720) to speed up image processing.


**–** Close other programs on your Pi to free up CPU and RAM.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**3.5. 17. Text Vision Talk with Ollama** **103**


**SunFounder PiCar-X Kit**

### **3.6 18. Connecting to Online LLMs**


In this lesson, we’ll learn how to connect your PiCar-X (or Raspberry Pi) to different **online Large Language Models**
**(LLMs)** . Each provider requires an API key and offers different models you can choose from.


We’ll cover how to:


  - Create and save your API keys safely.


  - Pick a model that fits your needs.


  - Run our example code to chat with the models.


Let’s go step by step for each provider.


**3.6.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.6.2 OpenAI**


OpenAI provides powerful models like **GPT-4o** and **GPT-4.1** that can be used for both text and vision tasks.


Here’s how to set it up:


**Get and Save your API Key**


1. Go to and log in. On the **API keys** page, click **Create new secret key** .


**104** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


2. Fill in the details (Owner, Name, Project, and permissions if needed), then click **Create secret key** .


3. Once the key is created, copy it right away — you won’t be able to see it again. If you lose it, you’ll need to
generate a new one.


**3.6. 18. Connecting to Online LLMs** **105**


**SunFounder PiCar-X Kit**


4. In your project folder (for example: `/picar-x/example` ), create a file called `secret.py` :





5. Paste your key into the file like this:





**Enable billing and check models**


1. Before using the key, go to the **Billing** page in your OpenAI account, add your payment details, and top up a
small amount of credits.


**106** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


2. Then go to the **Limits** page to check which models are available for your account and copy the exact model ID
to use in your code.


**Test with example code**


1. Open sample code:


**3.6. 18. Connecting to Online LLMs** **107**


**SunFounder PiCar-X Kit**





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example, `gpt-4o` ):

```
   from picarx.llm import OpenAI
   from secret import OPENAI_API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = OpenAI(
     api_key=OPENAI_API_KEY,
     model="gpt-4o",
   )

```

Save and exit ( `Ctrl+X`, then `Y`, then `Enter` ).


3. Finally, run the test:

```
   sudo python3 18.online_llm_test.py

```

**3.6.3 Gemini**


Gemini is Google’s family of AI models. It’s fast and great for general-purpose tasks.


**Get and Save your API Key**


1. Log in to, then go to the API Keys page.


**108** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


2. Click the **Create API key** button in the top-right corner.


3. You can create a key for an existing project or a new one.


**3.6. 18. Connecting to Online LLMs** **109**


**SunFounder PiCar-X Kit**


4. Copy the generated API key.


5. In your project folder:





6. Paste the key:





**Check available models**


Go to the official page, here you’ll see the list of models, their exact API IDs, and which use case each one is optimized
for.


**110** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**



**Test with example code**


1. Open the test file:





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example,
`gemini-2.5-flash` ):

```
   from picarx.llm import Gemini
   from secret import GEMINI_API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = Gemini(
     api_key=GEMINI_API_KEY,
     model="gemini-2.5-flash",
   )

```

3. Save and run:

```
   sudo python3 18.online_llm_test.py

```

**3.6. 18. Connecting to Online LLMs** **111**


**SunFounder PiCar-X Kit**


**3.6.4 Qwen**


Qwen is a family of large language and multimodal models provided by Alibaba Cloud. These models support text
generation, reasoning, and multimodal understanding (such as image analysis).


**Get an API Key**


To call Qwen models, you need an **API Key** . Most international users should use the **DashScope International (Model**
**Studio)** console. Mainland China users can instead use the **Bailian ()** console.


   - **For International Users**


1. Go to the official page on **Alibaba Cloud** .


2. Sign in or create an **Alibaba Cloud** account.


3. Navigate to **Model Studio** (choose Singapore or Beijing region).


**–** If an “Activate Now” prompt appears at the top of the page, click it to activate Model Studio and receive
the free quota (Singapore only).


**–** Activation is free — you will only be charged after your free quota is used.


**–** If no activation prompt appears, the service is already active.


4. Go to the **Key Management** page. On the **API Key** tab, click **Create API Key** .


5. After creation, copy your API Key and keep it safe.


**Note:** Users in Hong Kong, Macau, and Taiwan should also choose the **International (Model Studio)** option.


   - **For Mainland China Users**


If you are in Mainland China, you can use the **Alibaba Cloud Bailian ()** console instead:


1. Log in to (Bailian console) and complete account verification.


2. Select **Create API Key** . If prompted that model services are not activated, click **Activate**, agree to the
terms, and claim your free quota. After activation, the **Create API Key** button will be enabled.


**112** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


3. Click **Create API Key** again, check your account, and then click **Confirm** .


**3.6. 18. Connecting to Online LLMs** **113**


**SunFounder PiCar-X Kit**


4. Once created, copy your API Key.


**Save your API Key**


1. In your project folder:





2. Paste your key like this:


**114** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**



**Test with example code**


1. Open the test file:





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example,
`qwen-plus` ):

```
   from picarx.llm import Qwen
   from secret import QWEN_API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = Qwen(
     api_key=QWEN_API_KEY,
     model="qwen-plus",
   )

```

3. Run with:

```
   sudo python3 18.online_llm_test.py

```

**3.6.5 Grok (xAI)**


Grok is xAI’s conversational AI, created by Elon Musk’s team. You can connect to it through the xAI API.


**Get and Save your API Key**


1. Sign up for an account here: . Add some credits to your account first — otherwise the API won’t work.


2. Go to the API Keys page, click **Create API key** .


3. Enter a name for the key, then click **Create API key** .


**3.6. 18. Connecting to Online LLMs** **115**


**SunFounder PiCar-X Kit**


4. Copy the generated key and keep it safe.


5. In your project folder:


**116** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**





6. Paste your key like this:



**Check available models**


Go to the Models page in the xAI console. Here you can see all the models available to your team, along with their
exact API IDs — use these IDs in your code.


**Test with example code**


1. Open the test file:





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example,
`grok-4-latest` ):

```
   from picarx.llm import Grok
   from secret import GROK_API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
```

(continues on next page)


**3.6. 18. Connecting to Online LLMs** **117**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = Grok(
     api_key=GROK_API_KEY,
     model="grok-4-latest",
   )

```

3. Run with:

```
   sudo python3 18.online_llm_test.py

```

**3.6.6 DeepSeek**


DeepSeek is a Chinese LLM provider that offers affordable and capable models.


**Get and Save your API Key**


1. Log in to .


2. In the top-right menu, select **API Keys** _→_ **Create API Key** .


3. Enter a name, click **Create**, then copy the key.


**118** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**



4. In your project folder:





5. Add your key:





**Enable billing**


You’ll need to recharge your account first. Start with a small amount (like ¥10 RMB).


**Available models**


At the time of writing (2025-09-12), DeepSeek offers:


**3.6. 18. Connecting to Online LLMs** **119**


**SunFounder PiCar-X Kit**


   - `deepseek-chat`


   - `deepseek-reasoner`


**Test with example code**


1. Open the test file:





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example,
`deepseek-chat` ):



3. Run:

```
   sudo python3 18.online_llm_test.py

```

**3.6.7 Doubao**


Doubao is ByteDance’s AI model platform (Volcengine Ark).


**Get and Save your API Key**


1. Log in to .


2. In the left menu, scroll down to **API Key Management** _→_ **Create API Key** .


**120** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


3. Choose a name and click **Create** .


**3.6. 18. Connecting to Online LLMs** **121**


**SunFounder PiCar-X Kit**


4. Click the **Show API Key** icon and copy it.


5. In your project folder:





6. Add your key:





**Choose a model**


1. Go to the model marketplace and pick a model.


**122** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


2. For example, choose **Doubao-seed-1.6**, then click **API** .


**3.6. 18. Connecting to Online LLMs** **123**


**SunFounder PiCar-X Kit**


3. Select your API Key and click **Use API** .


**124** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


4. Click **Enable Model** .


5. Hover over the model ID to copy it.


**3.6. 18. Connecting to Online LLMs** **125**


**SunFounder PiCar-X Kit**


**Test with example code**


1. Open the test file:





2. Replace the content with the code below, and update `model="xxx"` to the model you want (for example,
`doubao-seed-1-6-250615` ):

```
   from picarx.llm import Doubao
   from secret import DOUBAO_API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = Doubao(
     api_key=DOUBAO_API_KEY,
     model="doubao-seed-1-6-250615",
   )

```

3. Run with:

```
   sudo python3 18.online_llm_test.py

```

**126** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**3.6.8 General**


This project supports connecting to multiple LLM platforms through a unified interface. We have built-in compatibility
with:


   - **OpenAI** (ChatGPT / GPT-4o, GPT-4, GPT-3.5)


   - **Gemini** (Google AI Studio / Vertex AI)


   - **Grok** (xAI)


   - **DeepSeek**


   - **Qwen ()**


   - **Doubao ()**


In addition, you can connect to **any other LLM service that is compatible with the OpenAI API format** . For those
platforms, you will need to manually obtain your **API Key** and the correct **base_url** .


**Get and Save Your API Key**


1. Obtain an **API Key** from the platform you want to use. (See each platform’s official console for details.)


2. In your project folder, create a new file:





3. Add your key into `secret.py` :





**Warning:** Keep your API Key private. Do not upload `secret.py` to public repositories.


**Test With Example Code**


1. Open the test file:





2. Replace the content of a Python file with the following example, and fill in the correct `base_url` and `model` for
your platform:


**Note:** About `base_url` : We support the **OpenAI API format**, as well as any API that is **compatible** with it.
Each provider has its own `base_url` . Please check their documentation.

```
   from picarx.llm import LLM
   from secret import API_KEY

   INSTRUCTIONS = "You are a helpful assistant."
   WELCOME = "Hello, I am a helpful assistant. How can I help you?"

   llm = LLM(
```

(continues on next page)


**3.6. 18. Connecting to Online LLMs** **127**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
     base_url="https://api.example.com/v1", # fill in your provider’s base_url
     api_key=API_KEY,
     model="your-model-name-here", # choose a model from your provider
   )

```

3. Run the program:

```
   python3 18.online_llm_test.py

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

### **3.7 19. Local Voice Chatbot**


In this lesson, you will combine everything you’ve learned — **speech recognition (STT)**, **text-to-speech (TTS)**, and
a **local LLM (Ollama)** - to build a fully offline **voice chatbot** that runs on your PiCar-X system.


The workflow is simple:


1. **Listen**  - The microphone captures your speech and transcribes it with **Vosk** .


2. **Think**  - The text is sent to a local **LLM** running on Ollama (e.g., `llama3.2:3b` ).


3. **Speak**  - The chatbot answers aloud using **Piper TTS** .


This creates a **hands-free conversational robot** that can understand and respond in real time.


**3.7.1 Before You Start**


Make sure you have prepared the following:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


  - Tested **Piper TTS** ( _1. Testing Piper_ ) and chosen a working voice model.


  - Tested **Vosk STT** ( _2. Test Vosk_ ) and chosen the right language pack (e.g., `en-us` ).


  - Installed **Ollama** ( _1. Install Ollama (LLM) and Download Model_ ) on your Pi or another computer, and downloaded a model such as `llama3.2:3b` (or a smaller one like `moondream:1.8b` if memory is limited).


**128** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**



**3.7.2 Run the Code**


1. Open the example script:





2. Update the parameters as needed:


    - `stt = Vosk(language="en-us")` : Change this to match your accent/language package (e.g., `en-us`,
`zh-cn`, `es` ).


    - `tts.set_model("en_US-amy-low")` : Replace with the Piper voice model you verified in _1. Testing_
_Piper_ .


    - `llm = Ollama(ip="localhost", model="llama3.2:3b")` : Update both `ip` and `model` to your own
setup.


**–** `ip` : If Ollama runs on the **same Pi**, use `localhost` . If Ollama runs on another computer in your LAN,
enable **Expose to network** in Ollama and set `ip` to that computer’s LAN IP.


**–** `model` : Must exactly match the model name you downloaded/activated in Ollama.


3. Run the script:





4. After running, you should see:


     - The bot greets you with a spoken welcome message.


     - It waits for speech input.


     - Vosk transcribes your speech into text.


     - The text is sent to Ollama, which streams back a reply.


     - The reply is cleaned (removing hidden reasoning) and spoken aloud by Piper.


     - Stop the program anytime with `Ctrl+C` .


**3.7.3 Code**



**3.7. 19. Local Voice Chatbot** **129**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
# Instructions for the LLM
INSTRUCTIONS = (
  "You are a helpful assistant. Answer directly in plain English. "
  "Do NOT include any hidden thinking, analysis, or tags like <think>."
)
WELCOME = "Hello! I'm your voice chatbot. Speak when you're ready."

# Initialize Ollama connection
llm = Ollama(ip="localhost", model="llama3.2:3b")
llm.set_max_messages(20)
llm.set_instructions(INSTRUCTIONS)

# Utility: clean hidden reasoning
def strip_thinking(text: str) -> str:
  if not text:
    return ""
  text = re.sub(r"<\s*think[^>]*>.*?<\s*/\s*think\s*>", "", text, flags=re.DOTALL|re.
```

_˓→_ `IGNORECASE)`
```
  text = re.sub(r"<\s*thinking[^>]*>.*?<\s*/\s*thinking\s*>", "", text, flags=re.
```

_˓→_ `DOTALL|re.IGNORECASE)`
```
  text = re.sub(r"���(?:\s*thinking)?\s*.*?���", "", text, flags=re.DOTALL|re.
```

_˓→_ `IGNORECASE)`
```
  text = re.sub(r"\[/?thinking\]", "", text, flags=re.IGNORECASE)
  return re.sub(r"\s+\n", "\n", text).strip()

def main():
  print(WELCOME)
  tts.say(WELCOME)

  try:
    while True:
      print("\n Listening... (Press Ctrl+C to stop)")

      # Collect final transcript from Vosk
      text = ""
      for result in stt.listen(stream=True):
        if result["done"]:
          text = result["final"].strip()
          print(f"[YOU] { text } ")
        else:
          print(f"[YOU] { result['partial'] } ", end="\r", flush=True)

      if not text:
        print("[INFO] Nothing recognized. Try again.")
        time.sleep(0.1)
        continue

      # Query Ollama with streaming
      reply_accum = ""
      response = llm.prompt(text, stream=True)
      for next_word in response:
        if next_word:

```

(continues on next page)


**130** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
          print(next_word, end="", flush=True)
          reply_accum += next_word
      print("")

      # Clean and speak
      clean = strip_thinking(reply_accum)
      if clean:
        tts.say(clean)
      else:
        tts.say("Sorry, I didn't catch that.")

      time.sleep(0.05)

  except KeyboardInterrupt:
    print("\n[INFO] Stopping...")
  finally:
    tts.say("Goodbye!")
    print("Bye.")

if __name__ == "__main__":
  main()

```

**3.7.4 Code Analysis**


**Imports and global setup**





Brings in the three subsystems you built earlier: **Vosk** for speech-to-text (STT), **Ollama** for the LLM, and **Piper** for
text-to-speech (TTS).


**Initialize STT (Vosk)**

```
stt = Vosk(language="en-us")

```

Loads the Vosk model for US English. Change the language code (e.g., `zh-cn`, `es` ) to match your voice pack for better
accuracy.


**Initialize TTS (Piper)**





Creates a Piper engine and selects a specific voice. Pick a model you’ve tested in _1. Testing Piper_ . Lower-quality
voices are faster and use less CPU.


**LLM instructions and welcome line**


**3.7. 19. Local Voice Chatbot** **131**


**SunFounder PiCar-X Kit**



Two key UX choices:


  - Keep **answers short and direct** (helps with TTS clarity).


  - Explicitly forbid hidden “chain-of-thought” tags to reduce noisy outputs.


**Connect to Ollama and set conversation scope**






   - `ip="localhost"` assumes the Ollama server runs on the same Pi. If it runs on another LAN machine, put that
computer’s **LAN IP** and enable _Expose to network_ in Ollama.


   - `set_max_messages(20)` keeps a short conversational history. Lower this if memory/latency is tight.


**Strip hidden reasoning / tags before speaking**







Some models may emit internal-style tags (e.g., `<think>...` ). This function removes those so your TTS **only** speaks
the final answer.


**Tip:** If you see other artifacts on screen (because you stream raw tokens), this function already ensures **spoken** output
stays clean.


**Main loop: greet once, then listen** _→_ **think** _→_ **speak**





Greets the user via terminal and speaker. Happens once at startup.


**Listen (streaming STT with live partials)**

```
print("\n Listening... (Press Ctrl+C to stop)")

text = ""
for result in stt.listen(stream=True):
  if result["done"]:
```

(continues on next page)


**132** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
    text = result["final"].strip()
    print(f"[YOU] { text } ")
  else:
    print(f"[YOU] { result['partial'] } ", end="\r", flush=True)

```

   - `stream=True` yields **partial** transcripts for immediate feedback and a **final** transcript when the utterance ends.


  - The final recognized text is stored in `text` and printed once.


**Guard:** If nothing was recognized, you skip the LLM call:



This avoids sending empty prompts to the model (saves time and tokens).


**Think (LLM) with streamed printing**

```
reply_accum = ""
response = llm.prompt(text, stream=True)
for next_word in response:
  if next_word:
    print(next_word, end="", flush=True)
    reply_accum += next_word
print("")

```

  - Sends the final transcript to the local LLM and **prints tokens as they arrive** for low latency.


  - Meanwhile, you accumulate the full reply in `reply_accum` for post-processing.


**Note:** If you’d rather **not** show raw tokens, set `stream=False` and just print the final string.


**Speak (clean first, then TTS once)**






  - Cleans the final text to remove hidden tags, then **speaks exactly once** .


  - Keeping TTS to a single pass avoids repeated prompts like “[LLM] / [SAY]”.


**Exit and teardown**





Use **Ctrl+C** to stop. The bot says a short goodbye to signal a clean exit.


**3.7. 19. Local Voice Chatbot** **133**


**SunFounder PiCar-X Kit**


**3.7.5 Troubleshooting & FAQ**


   - **Model is too large (memory error)**


Use a smaller model like `moondream:1.8b` or run Ollama on a more powerful computer.


   - **No response from Ollama**


Make sure Ollama is running ( `ollama serve` or desktop app open). If remote, enable **Expose to network** and
check IP address.


   - **Vosk not recognizing speech**


Verify your microphone works. Try another language pack ( `zh-cn`, `es` etc.) if needed.


   - **Piper silent or errors**


Confirm the chosen voice model is downloaded and tested in _1. Testing Piper_ .


   - **Answers too long or off-topic**


Edit `INSTRUCTIONS` to add: **“Keep answers short and to the point.”**


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **3.8 20. Treasure Hunt**


In this lesson, you will turn your PiCar-X into a **treasure hunter robot** . Arrange a maze in your room and place six
different color cards in different corners. Your PiCar-X will **search, recognize, and celebrate** when it finds the target
color.


This project combines three skills you’ve learned so far:


   - **Computer Vision**   - detecting colored cards with the Pi camera.


   - **Keyboard Control**   - driving the robot manually through the maze.


   - **Speech Feedback**   - Pico2Wave announces the target color and success.


It’s a fun game that shows how robots can **see, think, and act** just like treasure hunters!


**Note:** You can download and print the `PDF Color Cards` for reliable color detection.


**134** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**3.8.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


**3.8.2 Run the Code**





After running, you’ll see a message like this:

```
* Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

```

Then, open `http://<your IP>:9000/mjpg` in your browser to view the live video feed. Example: `http://192.`
```
168.18.113:9000/mjpg

```

**3.8.3 Game Rules**


1. The robot randomly selects a **target color** and says: **“Look for red!”**


2. You drive PiCar-X with the keyboard:


      - `w` = forward


      - `a` = turn left


      - `s` = backward


      - `d` = turn right


      - `space` = repeat target


      - `Ctrl+C` = quit


3. When the camera sees the target color card, PiCar-X says **“Well done!”**


4. A new target color is chosen, and the hunt continues!


**3.8.4 Code**

```
#!/usr/bin/env python3

from picarx import Picarx
from vilib import Vilib
from picarx.tts import Pico2Wave

from time import sleep
```

(continues on next page)


**3.8. 20. Treasure Hunt** **135**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
import threading
import readchar
import random

# ----------------------# Settings
# ----------------------COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
DETECTION_WIDTH_THRESHOLD = 100 # how wide the color blob must be
DRIVE_SPEED = 80
TURN_ANGLE = 30

MANUAL = """
Press keys to control PiCar-X:
 w: forward a: turn left s: backward d: turn right
 space: repeat target Ctrl+C: quit
"""

# ----------------------# Init
# ----------------------px = Picarx()

tts = Pico2Wave()
tts.set_lang("en-US")

current_color = "red"
key = None
lock = threading.Lock()

def say(line: str):
  print(f"[SAY] { line } ")
  tts.say(line)

def renew_color_detect():
  """Choose a new target color and start detection."""
  global current_color
  current_color = random.choice(COLORS)
  Vilib.color_detect(current_color)
  say(f"Look for { current_color } !")

def key_scan_thread():
  """Background thread reading keys."""
  global key
  while True:
    k = readchar.readkey()
    # Map special keys before lowercasing
    if k == readchar.key.SPACE:
      mapped = "space"
    elif k == readchar.key.CTRL_C:
      mapped = "quit"
    else:

```

(continues on next page)


**136** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
      mapped = k.lower()

    with lock:
      key = mapped

    if mapped == "quit":
      return
    sleep(0.01)

def car_move(k: str):
  if k == "w":
    px.set_dir_servo_angle(0)
    px.forward(DRIVE_SPEED)
  elif k == "s":
    px.set_dir_servo_angle(0)
    px.backward(DRIVE_SPEED)
  elif k == "a":
    px.set_dir_servo_angle(-TURN_ANGLE)
    px.forward(DRIVE_SPEED)
  elif k == "d":
    px.set_dir_servo_angle(TURN_ANGLE)
    px.forward(DRIVE_SPEED)

def main():
  global key

  # Start camera and web preview
  Vilib.camera_start(vflip=False, hflip=False)
  Vilib.display(local=False, web=True)
  sleep(0.8)

  print(MANUAL.strip())
  say("Game start!")
  sleep(0.1)
  renew_color_detect()

  # Start keyboard thread (modern style)
  key_thread = threading.Thread(target=key_scan_thread, daemon=True)
  key_thread.start()

  try:
    while True:
      # Check detection: if target color present and wide enough
      if (Vilib.detect_obj_parameter.get("color_n", 0) != 0 and
        Vilib.detect_obj_parameter.get("color_w", 0) > DETECTION_WIDTH_
```

_˓→_ `THRESHOLD):`
```
        say("Well done!")
        sleep(0.1)
        renew_color_detect()

      # Take a snapshot of the last key (and clear it)
      with lock:

```

(continues on next page)


**3.8. 20. Treasure Hunt** **137**


**SunFounder PiCar-X Kit**


(continued from previous page)

```
        k = key
        key = None

      # Handle movement / actions
      if k in ("w", "a", "s", "d"):
        car_move(k)
        sleep(0.5)
        px.stop()
      elif k == "space":
        say(f"Look for { current_color } !")
      elif k == "quit":
        print("\n[INFO] Quit requested.")
        break

      sleep(0.05)

  except KeyboardInterrupt:
    print("\n[INFO] Stopped by user.")
  finally:
    try:
      Vilib.camera_close()
    except Exception:
      pass
    px.stop()
    say("Goodbye!")
    sleep(0.2)

if __name__ == "__main__":
  main()

```

**3.8.5 How It Works**


1. **Initialization**


     - Import modules and configure PiCar-X, camera, and TTS.


     - Set color list, speed, and steering angle.


2. **Target Selection**


      - `renew_color_detect()` randomly picks a target color.


     - The robot announces the target with Pico2Wave.


3. **Keyboard Control**


      - `key_scan_thread()` runs in the background to capture keys.


    - Keys `w, a, s, d` control motion; `space` repeats target.


4. **Color Detection**


     - Camera constantly checks if the target color is visible.


     - If the detected blob is large enough, PiCar-X celebrates.


5. **Main Loop**


**138** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


     - Continuously handles movement, detection, and feedback.


     - Cleanly stops the robot and camera when quitting.


**3.8.6 Troubleshooting**


   - **Camera feed not working?**


Run `libcamera-hello` to check if the Pi camera is connected properly.


   - **Robot doesn’t detect colors?**


Ensure the cards are printed clearly and placed in good lighting. Try adjusting `DETECTION_WIDTH_THRESHOLD` .


   - **No voice feedback?**


Check that `pico2wave` is installed and your audio output is configured.


   - **Car doesn’t move?**


Verify PiCar-X power is on and the motor calibration is correct.


By completing this lesson, you’ve built a **mini treasure hunt game** with PiCar-X, combining **vision, control, and**
**interaction** into one project!


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!

### **3.9 21. AI Voice Assistant Car**


This lesson turns your PiCar-X into an **AI-powered voice assistant on wheels** . The robot can wake up to your voice,
recognize what you say, talk back with emotion, and act out its “feelings” through movements, gestures, and lights.


You’ll build a **fully interactive voice assistant car** using:


   - **LLM**   - Large Language Model (OpenAI GPT or Doubao).


   - **STT**   - Speech-to-Text (voice to text).


   - **TTS**   - Text-to-Speech (text to voice).


   - **Sensors + Actions**   - Ultrasonic, camera, and built-in expressive actions.


**3.9. 21. AI Voice Assistant Car** **139**


**SunFounder PiCar-X Kit**


**3.9.1 Before You Start**


Make sure you‘ve completed:


   - _Install All the Modules (Important)_   - Install `robot-hat`, `vilib`, `picar-x` modules, then run the script
`i2samp.sh` .


   - _1. Testing Piper_   - Check the supported languages of **Piper TTS** .


   - _2. Test Vosk_   - Check the supported languages of **Vosk STT** .


   - _18. Connecting to Online LLMs_   - This step is **very important** : obtain your **OpenAI** or **Doubao** API key, or
the API key for any other supported LLM.


You should already have:


  - A working **microphone** and **speaker** on your PiCar-X.


  - A **valid API key** stored in `secret.py` .


  - A stable network connection (a **wired connection** is recommended for better stability).


**3.9.2 Run the Example**


Both language versions are placed in the same directory:

```
cd ~/picar-x/example

```

**English version** (OpenAI GPT, instructions in English):

```
sudo python3 21.voice_active_car_gpt.py

```

  - LLM: `OpenAI GPT-4o-mini`


  - TTS: `en_US-ryan-low` (Piper)


  - STT: Vosk ( `en-us` )


Wake word:

```
"Hey buddy"

```



**Chinese version** (Doubao, instructions in Chinese):

```
sudo python3 21.voice_active_car_doubao_cn.py

```

  - LLM: `Doubao-seed-1-6-250615`


  - TTS: `zh_CN-huayan-x_low` (Piper)


  - STT: Vosk ( `cn` )


Wake word:

```
" "

```

**140** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**Note:** You can modify the **wake word** and **robot name** in the code: `NAME = "Buddy"` or `NAME = "" WAKE_WORD =`

`["hey buddy"]` or `WAKE_WORD = [" "]`


**3.9.3 What Will Happen**


When you run this example successfully:


  - The robot **waits for the wake word** (e.g., “Hey Buddy” / “ ”).


  - When it hears the wake word:


**–** LEDs will **blink** and stay on.


**–** The robot **greets you** with a cheerful voice.


   - It then starts **listening to your voice** in real time.


  - After recognizing what you said, it:


**–** Sends your speech to the **LLM** (OpenAI or Doubao).


**– Thinks** and blinks LED while processing.


**–** Replies with **TTS voice** .


**–** Executes **corresponding actions** (e.g., nodding, turning, celebrating).


  - If you approach it too closely, the ultrasonic sensor:


**–** Triggers an auto **backward** move for safety.


**–** Interrupts the current round with a warning response.


**Example interaction**


**3.9.4 Switching to Other LLMs or TTS**


You can easily switch to other LLMs, TTS, or STT languages with just a few edits:


  - Supported LLMs:


**–** OpenAI


**–** Doubao


**–** Deepseek


**–** Gemini


**–** Qwen


**3.9. 21. AI Voice Assistant Car** **141**


**SunFounder PiCar-X Kit**


**–** Grok


   - _1. Testing Piper_   - Check the supported languages of **Piper TTS** .


   - _2. Test Vosk_   - Check the supported languages of **Vosk STT** .


To switch, simply modify the initialization part in the code:



**3.9.5 Action & Sound Reference**


Below are the **action keywords** the LLM can return (after the `ACTIONS:` line) and what they do on the robot.





















**Movement & Utility**


**142** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**SunFounder PiCar-X Kit**


**Sound Effects**


**Sensor Triggers (Automatic)**


   - **Ultrasonic proximity**


**–** Trigger: distance < 10 cm


**–** Side effect: auto `backward` + disable image for this round


**–** Injected message: `<<<Ultrasonic sense too close:` `{distance}cm>>>`


**Lifecycle Hooks (LED Indicators)**


   - `before_listen` _→_ blink twice (ready to listen)


   - `before_think` _→_ blinking (thinking)


   - `before_say` _→_ LED on (speaking)


   - `after_say` _→_ wait for actions _→_ LED off


   - `on_stop` _→_ stop actions, close devices


**3.9.6 Troubleshooting**


   - **The robot doesn’t respond to wake word**


**–** Check if the microphone works.


**–** Ensure `WAKE_ENABLE = True` .


**–** Adjust wake word to match your pronunciation.


   - **No sound from the speaker**


**–** Verify TTS model setup.


**–** Test Piper or Espeak manually.


**–** Check speaker connection and volume.


   - **API Key error or timeout**


**–** Check your key in `secret.py` .


**–** Ensure network connection.


**–** Confirm the LLM is supported.


   - **Picar-X doesn’t move or act**


**3.9. 21. AI Voice Assistant Car** **143**


**SunFounder PiCar-X Kit**


**–** Check that the action name matches `actions_dict` .


**–** Verify motor and servo connections.


   - **Ultrasonic sensor keeps triggering unexpectedly.**


**–** Check sensor installation height and angle.


**–** Adjust the `TOO_CLOSE` distance threshold in code.


**Note:** Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook!
Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.


**Why Join?**


   - **Expert Support** : Solve post-sale issues and technical challenges with help from our community and team.


   - **Learn & Share** : Exchange tips and tutorials to enhance your skills.


   - **Exclusive Previews** : Get early access to new product announcements and sneak peeks.


   - **Special Discounts** : Enjoy exclusive discounts on our newest products.


   - **Festive Promotions and Giveaways** : Take part in giveaways and holiday promotions.


Ready to explore and create with us? Click [] and join today!


**144** **Chapter 3. Think · Talk · Drive — AI-Powered with Multi-LLMs**


**CHAPTER**
