#!/usr/bin/env python3
"""
PiCar-X Web Control met YOLO Object Detection

Start: python3 nerdcarx_web.py
Open:  http://<pi-ip>:5000

Features:
- WASD besturing met physics (acceleratie, remmen, friction)
- IJKL of buttons voor camera pan/tilt
- Night/Day camera mode
- YOLO object detection met bounding boxes in de stream
"""

from flask import Flask, render_template_string, request, jsonify, Response
from picarx import Picarx
from vilib import Vilib
from threading import Thread, Lock
from time import sleep, time
import socket
import cv2
import numpy as np

# === YOLO SETUP ===
# Probeer YOLO te laden, anders werkt het script nog steeds maar zonder detection
YOLO_AVAILABLE = False
yolo_model = None

try:
    from ultralytics import YOLO
    print("Loading YOLO model...")
    # yolov8n.pt = nano model, klein en snel voor Pi
    yolo_model = YOLO('yolov8n.pt')
    YOLO_AVAILABLE = True
    print("YOLO loaded successfully!")
except ImportError:
    print("WARNING: ultralytics not installed. Run: pip install ultralytics")
    print("Continuing without YOLO detection...")
except Exception as e:
    print(f"WARNING: Could not load YOLO: {e}")
    print("Continuing without YOLO detection...")

app = Flask(__name__)
px = Picarx()

# === STATE ===
speed = 0
steer_angle = 0
cam_pan = 0
cam_tilt = 0
camera_mode = 'night'
yolo_enabled = True  # Toggle voor YOLO aan/uit

# === YOLO DETECTION STATE ===
# Wordt geupdate door de detection thread
yolo_detections = []
yolo_lock = Lock()
yolo_fps = 0

# === CAMERA PRESETS ===
NIGHT_MODE = {
    'AeEnable': False,
    'ExposureValue': 1.0,
    'Brightness': 0.1,
    'AnalogueGain': 57.0,
    'ExposureTime': 35134,
    'Contrast': 1.0,
    'Saturation': 1.0,
}

DAY_MODE = {
    'AeEnable': True,
    'ExposureValue': 0.0,
    'Brightness': 0.0,
    'AnalogueGain': 1.0,
    'ExposureTime': 20000,
    'Contrast': 1.0,
    'Saturation': 1.0,
}

# === PHYSICS ===
ACCELERATION = 8
BRAKE_POWER = 12
FRICTION = 3
MAX_SPEED = 80
STEER_SPEED = 8
STEER_CENTER_SPEED = 4
MAX_STEER = 35

# Keys currently pressed (from browser)
keys = set()

# === YOLO DETECTION LOOP ===
def yolo_detection_loop():
    """Draait YOLO detection op frames van Vilib.img"""
    global yolo_detections, yolo_fps

    if not YOLO_AVAILABLE:
        return

    last_time = time()
    frame_count = 0

    while True:
        if not yolo_enabled:
            sleep(0.1)
            continue

        try:
            # Pak frame van vilib
            frame = Vilib.img
            if frame is None:
                sleep(0.1)
                continue

            # Run YOLO inference
            results = yolo_model(frame, verbose=False, conf=0.5)

            # Parse resultaten
            detections = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf)
                    cls = int(box.cls)
                    label = yolo_model.names[cls]

                    detections.append({
                        'label': label,
                        'confidence': conf,
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2)
                    })

            # Update global state (thread-safe)
            with yolo_lock:
                yolo_detections = detections

            # Calculate FPS
            frame_count += 1
            if frame_count >= 10:
                now = time()
                yolo_fps = frame_count / (now - last_time)
                last_time = now
                frame_count = 0

            # ~5 FPS voor YOLO op Pi (aanpasbaar)
            sleep(0.2)

        except Exception as e:
            print(f"YOLO error: {e}")
            sleep(1)


def generate_frames():
    """Generator voor MJPEG stream met YOLO bounding boxes"""
    while True:
        try:
            # Pak frame van vilib
            frame = Vilib.img
            if frame is None:
                sleep(0.05)
                continue

            # Maak een kopie om op te tekenen
            frame = frame.copy()

            # Teken YOLO boxes als enabled
            if yolo_enabled and YOLO_AVAILABLE:
                with yolo_lock:
                    detections = yolo_detections.copy()

                for det in detections:
                    x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
                    label = det['label']
                    conf = det['confidence']

                    # Groene box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Label met achtergrond
                    text = f"{label} {conf:.0%}"
                    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), (0, 255, 0), -1)
                    cv2.putText(frame, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # FPS indicator
            if YOLO_AVAILABLE:
                status = f"YOLO: {'ON' if yolo_enabled else 'OFF'} | {yolo_fps:.1f} FPS"
            else:
                status = "YOLO: NOT INSTALLED"
            cv2.putText(frame, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Encode als JPEG
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            # ~20 FPS voor stream
            sleep(0.05)

        except Exception as e:
            print(f"Stream error: {e}")
            sleep(0.1)


HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PiCar-X + YOLO</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #1a1a2e;
            color: #eee;
            font-family: monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            min-height: 100vh;
        }
        h1 { color: #00d4ff; margin-bottom: 10px; }
        .container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .video-box {
            border: 2px solid #00d4ff;
            border-radius: 8px;
            overflow: hidden;
        }
        .video-box img {
            display: block;
            max-width: 640px;
            width: 100%;
        }
        .controls {
            background: #16213e;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #00d4ff;
            max-width: 280px;
        }
        .status {
            background: #0f0f23;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .meter { margin: 5px 0; }
        .meter-bar {
            background: #333;
            height: 18px;
            border-radius: 3px;
            overflow: hidden;
        }
        .meter-fill {
            background: #00d4ff;
            height: 100%;
            transition: width 0.05s;
        }
        .meter-fill.reverse { background: #ff6b6b; }
        .keys {
            display: grid;
            grid-template-columns: repeat(3, 45px);
            gap: 4px;
            justify-content: center;
            margin-top: 12px;
        }
        .key {
            background: #333;
            border: 2px solid #555;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.1s;
        }
        .key.active { background: #00d4ff; color: #000; border-color: #00d4ff; }
        .key.empty { visibility: hidden; }
        .label {
            text-align: center;
            color: #888;
            font-size: 10px;
            margin: 8px 0 4px 0;
        }
        .cam-grid {
            display: grid;
            grid-template-columns: repeat(3, 38px);
            gap: 3px;
            justify-content: center;
        }
        .cam-btn {
            background: #333;
            border: 2px solid #555;
            border-radius: 5px;
            padding: 6px;
            color: #eee;
            font-family: monospace;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.1s;
        }
        .cam-btn:hover { border-color: #00d4ff; }
        .cam-btn:active { background: #00d4ff; color: #000; }
        .btn-row {
            display: flex;
            gap: 6px;
            justify-content: center;
            margin-top: 8px;
        }
        .mode-btn {
            padding: 8px 14px;
            border: 2px solid #555;
            border-radius: 5px;
            background: #333;
            color: #eee;
            font-family: monospace;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .mode-btn:hover { border-color: #00d4ff; }
        .mode-btn.active { background: #00d4ff; color: #000; border-color: #00d4ff; }
        .mode-btn.night.active { background: #6b5bff; border-color: #6b5bff; }
        .mode-btn.yolo.active { background: #44ff44; border-color: #44ff44; color: #000; }
        .detect-list {
            background: #0f0f23;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 11px;
            max-height: 150px;
            overflow-y: auto;
        }
        .detect-item {
            padding: 3px 0;
            border-bottom: 1px solid #333;
        }
        .detect-item:last-child { border-bottom: none; }
        .detect-label { color: #44ff44; }
        .detect-conf { color: #888; }
    </style>
</head>
<body>
    <h1>PiCar-X + YOLO</h1>
    <div class="container">
        <div class="video-box">
            <img id="stream" src="/video_feed" alt="Camera Stream">
        </div>
        <div class="controls">
            <div class="status">
                <div class="meter">
                    <div>Speed: <span id="speed-val">0</span></div>
                    <div class="meter-bar">
                        <div class="meter-fill" id="speed-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="meter">
                    <div>Steer: <span id="steer-val">0</span>deg</div>
                    <div class="meter-bar" style="position: relative;">
                        <div style="position:absolute;left:50%;width:2px;height:100%;background:#fff"></div>
                        <div class="meter-fill" id="steer-bar" style="width: 4px; margin-left: 50%;"></div>
                    </div>
                </div>
            </div>

            <div class="keys">
                <div class="key empty"></div>
                <div class="key" id="key-w">W</div>
                <div class="key empty"></div>
                <div class="key" id="key-a">A</div>
                <div class="key" id="key-s">S</div>
                <div class="key" id="key-d">D</div>
            </div>
            <div class="label">WASD = rijden</div>

            <div class="label">Camera Pan/Tilt (of IJKL)</div>
            <div class="cam-grid">
                <div class="key empty"></div>
                <button class="cam-btn" onclick="camTilt(5)">Up</button>
                <div class="key empty"></div>
                <button class="cam-btn" onclick="camPan(-5)">L</button>
                <button class="cam-btn" onclick="camCenter()" style="font-size:9px">CTR</button>
                <button class="cam-btn" onclick="camPan(5)">R</button>
                <div class="key empty"></div>
                <button class="cam-btn" onclick="camTilt(-5)">Dn</button>
                <div class="key empty"></div>
            </div>
            <div class="label">Pan: <span id="pan-val">0</span> | Tilt: <span id="tilt-val">0</span></div>

            <div class="label">Camera Mode</div>
            <div class="btn-row">
                <button class="mode-btn night" id="btn-night" onclick="setMode('night')">Night</button>
                <button class="mode-btn day" id="btn-day" onclick="setMode('day')">Day</button>
            </div>

            <div class="label">YOLO Detection</div>
            <div class="btn-row">
                <button class="mode-btn yolo" id="btn-yolo" onclick="toggleYolo()">YOLO ON</button>
            </div>

            <div class="detect-list" id="detect-list">
                <div style="color:#888">Waiting for detections...</div>
            </div>
        </div>
    </div>

    <script>
        const keys = new Set();
        const validKeys = ['w', 'a', 's', 'd', 'i', 'j', 'k', 'l'];

        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (validKeys.includes(key) && !keys.has(key)) {
                keys.add(key);
                updateKeys();
            }
        });

        document.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            if (keys.has(key)) {
                keys.delete(key);
                updateKeys();
            }
        });

        window.addEventListener('blur', () => {
            keys.clear();
            updateKeys();
        });

        function updateKeys() {
            validKeys.forEach(k => {
                const el = document.getElementById('key-' + k);
                if (el) el.classList.toggle('active', keys.has(k));
            });
            fetch('/keys', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({keys: Array.from(keys)})
            });
        }

        function camPan(delta) {
            fetch('/camera/pan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({delta: delta})
            });
        }

        function camTilt(delta) {
            fetch('/camera/tilt', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({delta: delta})
            });
        }

        function camCenter() {
            fetch('/camera/center', {method: 'POST'});
        }

        function setMode(mode) {
            fetch('/camera_mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            });
        }

        function toggleYolo() {
            fetch('/yolo/toggle', {method: 'POST'});
        }

        setInterval(async () => {
            const resp = await fetch('/status');
            const data = await resp.json();

            document.getElementById('speed-val').textContent = Math.abs(data.speed).toFixed(0);
            document.getElementById('steer-val').textContent = data.steer.toFixed(0);
            document.getElementById('pan-val').textContent = data.cam_pan.toFixed(0);
            document.getElementById('tilt-val').textContent = data.cam_tilt.toFixed(0);

            const speedBar = document.getElementById('speed-bar');
            speedBar.style.width = (Math.abs(data.speed) / 80 * 100) + '%';
            speedBar.classList.toggle('reverse', data.speed < 0);

            const steerBar = document.getElementById('steer-bar');
            const steerPct = (data.steer / 35) * 50;
            steerBar.style.width = Math.abs(steerPct) + '%';
            steerBar.style.marginLeft = steerPct >= 0 ? '50%' : (50 + steerPct) + '%';

            document.getElementById('btn-night').classList.toggle('active', data.camera_mode === 'night');
            document.getElementById('btn-day').classList.toggle('active', data.camera_mode === 'day');

            const yoloBtn = document.getElementById('btn-yolo');
            yoloBtn.classList.toggle('active', data.yolo_enabled);
            yoloBtn.textContent = data.yolo_enabled ? 'YOLO ON' : 'YOLO OFF';

            // Detection list
            const list = document.getElementById('detect-list');
            if (data.detections.length === 0) {
                list.innerHTML = '<div style="color:#888">No objects detected</div>';
            } else {
                list.innerHTML = data.detections.map(d =>
                    `<div class="detect-item"><span class="detect-label">${d.label}</span> <span class="detect-conf">${(d.confidence * 100).toFixed(0)}%</span></div>`
                ).join('');
            }
        }, 200);

        document.getElementById('btn-night').classList.add('active');
        document.getElementById('btn-yolo').classList.add('active');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    """MJPEG stream met YOLO overlay"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/keys', methods=['POST'])
def update_keys():
    global keys
    data = request.json
    keys = set(data.get('keys', []))
    return jsonify({'ok': True})

@app.route('/camera_mode', methods=['POST'])
def set_camera_mode():
    global camera_mode
    data = request.json
    mode = data.get('mode', 'day')

    if mode == 'night':
        preset = NIGHT_MODE
    else:
        preset = DAY_MODE

    camera_mode = mode

    try:
        Vilib.set_controls({'AeEnable': preset['AeEnable']})
        sleep(0.1)
        for key, value in preset.items():
            if key != 'AeEnable':
                Vilib.set_controls({key: value})
    except Exception as e:
        print(f"Camera mode error: {e}")

    return jsonify({'ok': True, 'mode': mode})

@app.route('/status')
def status():
    with yolo_lock:
        detections = yolo_detections.copy()

    return jsonify({
        'speed': speed,
        'steer': steer_angle,
        'cam_pan': cam_pan,
        'cam_tilt': cam_tilt,
        'camera_mode': camera_mode,
        'yolo_enabled': yolo_enabled,
        'yolo_available': YOLO_AVAILABLE,
        'yolo_fps': yolo_fps,
        'detections': detections
    })

@app.route('/yolo/toggle', methods=['POST'])
def toggle_yolo():
    global yolo_enabled
    yolo_enabled = not yolo_enabled
    return jsonify({'ok': True, 'enabled': yolo_enabled})

@app.route('/camera/pan', methods=['POST'])
def set_pan():
    global cam_pan
    data = request.json
    delta = data.get('delta', 0)
    cam_pan += delta
    cam_pan = max(-30, min(30, cam_pan))
    px.set_cam_pan_angle(int(cam_pan))
    return jsonify({'ok': True, 'pan': cam_pan})

@app.route('/camera/tilt', methods=['POST'])
def set_tilt():
    global cam_tilt
    data = request.json
    delta = data.get('delta', 0)
    cam_tilt += delta
    cam_tilt = max(-30, min(30, cam_tilt))
    px.set_cam_tilt_angle(int(cam_tilt))
    return jsonify({'ok': True, 'tilt': cam_tilt})

@app.route('/camera/center', methods=['POST'])
def center_camera():
    global cam_pan, cam_tilt
    cam_pan = 0
    cam_tilt = 0
    px.set_cam_pan_angle(0)
    px.set_cam_tilt_angle(0)
    return jsonify({'ok': True})

def physics_loop():
    global speed, steer_angle, cam_pan, cam_tilt

    while True:
        # === GAS / REM ===
        if 'w' in keys:
            speed += ACCELERATION
            if speed > MAX_SPEED:
                speed = MAX_SPEED
        elif 's' in keys:
            if speed > 0:
                speed -= BRAKE_POWER
                if speed < 0:
                    speed = 0
            else:
                speed -= ACCELERATION
                if speed < -MAX_SPEED // 2:
                    speed = -MAX_SPEED // 2
        else:
            if speed > 0:
                speed -= FRICTION
                if speed < 0:
                    speed = 0
            elif speed < 0:
                speed += FRICTION
                if speed > 0:
                    speed = 0

        # === STUREN ===
        if 'a' in keys:
            steer_angle -= STEER_SPEED
            if steer_angle < -MAX_STEER:
                steer_angle = -MAX_STEER
        elif 'd' in keys:
            steer_angle += STEER_SPEED
            if steer_angle > MAX_STEER:
                steer_angle = MAX_STEER
        else:
            if steer_angle > 0:
                steer_angle -= STEER_CENTER_SPEED
                if steer_angle < 0:
                    steer_angle = 0
            elif steer_angle < 0:
                steer_angle += STEER_CENTER_SPEED
                if steer_angle > 0:
                    steer_angle = 0

        # === CAMERA via keyboard ===
        if 'i' in keys:
            cam_tilt += 2
            if cam_tilt > 30:
                cam_tilt = 30
        if 'k' in keys:
            cam_tilt -= 2
            if cam_tilt < -30:
                cam_tilt = -30
        if 'j' in keys:
            cam_pan -= 2
            if cam_pan < -30:
                cam_pan = -30
        if 'l' in keys:
            cam_pan += 2
            if cam_pan > 30:
                cam_pan = 30

        # === APPLY TO CAR ===
        px.set_dir_servo_angle(int(steer_angle))
        px.set_cam_pan_angle(int(cam_pan))
        px.set_cam_tilt_angle(int(cam_tilt))

        if speed > 0:
            px.forward(int(speed))
        elif speed < 0:
            px.backward(int(abs(speed)))
        else:
            px.stop()

        sleep(0.05)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def apply_camera_preset(preset):
    try:
        Vilib.set_controls({'AeEnable': preset['AeEnable']})
        sleep(0.1)
        for key, value in preset.items():
            if key != 'AeEnable':
                Vilib.set_controls({key: value})
    except Exception as e:
        print(f"Camera preset error: {e}")

if __name__ == '__main__':
    # Start camera via vilib (die doet de picamera2 setup)
    print("Starting camera...")
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=False)  # We maken onze eigen stream
    sleep(2)

    # Apply night mode settings
    apply_camera_preset(NIGHT_MODE)

    # Start physics loop
    physics_thread = Thread(target=physics_loop, daemon=True)
    physics_thread.start()

    # Start YOLO detection loop (als beschikbaar)
    if YOLO_AVAILABLE:
        yolo_thread = Thread(target=yolo_detection_loop, daemon=True)
        yolo_thread.start()
        print("YOLO detection thread started")

    ip = get_ip()
    print(f"\n" + "="*50)
    print(f"  Open in browser: http://{ip}:5000")
    print(f"  YOLO: {'ENABLED' if YOLO_AVAILABLE else 'NOT INSTALLED'}")
    print(f"="*50 + "\n")

    try:
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
    finally:
        px.stop()
        Vilib.camera_close()
