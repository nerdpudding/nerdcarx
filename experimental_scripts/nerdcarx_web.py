#!/usr/bin/env python3
"""
PiCar-X Web Control met YOLO Object Detection (Pi 5 Optimized)

Start: python3 nerdcarx_web.py
Open:  http://<pi-ip>:5000

Features:
- WASD besturing met physics (acceleratie, remmen, friction)
- IJKL of buttons voor camera pan/tilt
- Night/Day camera mode
- YOLO object detection met model selectie (nano/small/medium)
- CLAHE preprocessing voor betere low-light detectie
- Instelbare confidence threshold
"""

from flask import Flask, render_template_string, request, jsonify, Response
from picarx import Picarx
from vilib import Vilib
from threading import Thread, Lock
from time import sleep, time
import socket
import cv2

# === YOLO SETUP ===
YOLO_AVAILABLE = False
yolo_model = None
current_model_name = 'yolo11s.pt'  # Default: v11 small - beste balans

# Beschikbare modellen (voor Pi 5 16GB)
# YOLOv11 is nieuwer, lichter EN accurater dan v8
AVAILABLE_MODELS = {
    # YOLOv11 - aanbevolen (nieuwer, beter)
    'v11-nano': 'yolo11n.pt',    # ~5MB, snelste, 39.5% mAP
    'v11-small': 'yolo11s.pt',   # ~19MB, goed compromis, 47.0% mAP
    'v11-medium': 'yolo11m.pt',  # ~39MB, accuraat, 51.5% mAP
    # YOLOv8 - oudere versie
    'v8-nano': 'yolov8n.pt',     # ~6MB, 37.3% mAP
    'v8-small': 'yolov8s.pt',    # ~22MB, 44.9% mAP
    'v8-medium': 'yolov8m.pt',   # ~52MB, 50.2% mAP
}

try:
    from ultralytics import YOLO
    print(f"Loading YOLO model: {current_model_name}")
    yolo_model = YOLO(current_model_name)
    YOLO_AVAILABLE = True
    print("YOLO loaded successfully!")
except ImportError:
    print("WARNING: ultralytics not installed. Run: pip install ultralytics")
except Exception as e:
    print(f"WARNING: Could not load YOLO: {e}")

app = Flask(__name__)
px = Picarx()

# === STATE ===
speed = 0
steer_angle = 0
cam_pan = 0
cam_tilt = 0
camera_mode = 'night'
yolo_enabled = True

# === YOLO SETTINGS ===
yolo_confidence = 0.35      # Lagere threshold voor betere detectie
yolo_preprocess = True      # CLAHE preprocessing aan/uit
yolo_model_size = 'v11-small'  # v11-nano/v11-small/v11-medium/v8-nano/v8-small/v8-medium

# === YOLO DETECTION STATE ===
yolo_detections = []
yolo_lock = Lock()
yolo_fps = 0
yolo_inference_ms = 0

# === CLAHE voor low-light enhancement ===
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

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

keys = set()


def preprocess_frame(frame):
    """CLAHE preprocessing voor betere contrast in low-light"""
    if not yolo_preprocess:
        return frame

    try:
        # Convert naar LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        # Split kanalen
        l, a, b = cv2.split(lab)
        # Apply CLAHE op L-kanaal (luminance)
        l = clahe.apply(l)
        # Merge terug
        lab = cv2.merge([l, a, b])
        # Convert terug naar BGR
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    except Exception as e:
        print(f"Preprocess error: {e}")
        return frame


def yolo_detection_loop():
    """Draait YOLO detection op frames van Vilib.img"""
    global yolo_detections, yolo_fps, yolo_inference_ms

    if not YOLO_AVAILABLE:
        return

    last_time = time()
    frame_count = 0

    while True:
        if not yolo_enabled:
            sleep(0.1)
            continue

        try:
            frame = Vilib.img
            if frame is None:
                sleep(0.1)
                continue

            # Preprocessing voor betere detectie
            processed = preprocess_frame(frame)

            # Run YOLO inference
            t_start = time()
            results = yolo_model(
                processed,
                verbose=False,
                conf=yolo_confidence,
                imgsz=640,  # Standaard resolutie
            )
            yolo_inference_ms = (time() - t_start) * 1000

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

            with yolo_lock:
                yolo_detections = detections

            # Calculate FPS
            frame_count += 1
            if frame_count >= 5:
                now = time()
                yolo_fps = frame_count / (now - last_time)
                last_time = now
                frame_count = 0

            # Kleine pauze om CPU te sparen
            sleep(0.05)

        except Exception as e:
            print(f"YOLO error: {e}")
            sleep(1)


def generate_frames():
    """Generator voor MJPEG stream met YOLO bounding boxes"""
    while True:
        try:
            frame = Vilib.img
            if frame is None:
                sleep(0.05)
                continue

            frame = frame.copy()

            # Teken YOLO boxes
            if yolo_enabled and YOLO_AVAILABLE:
                with yolo_lock:
                    detections = yolo_detections.copy()

                for det in detections:
                    x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
                    label = det['label']
                    conf = det['confidence']

                    # Box kleur op basis van confidence
                    if conf > 0.7:
                        color = (0, 255, 0)  # Groen - hoge confidence
                    elif conf > 0.5:
                        color = (0, 255, 255)  # Geel - medium
                    else:
                        color = (0, 165, 255)  # Oranje - lage confidence

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # Label met achtergrond
                    text = f"{label} {conf:.0%}"
                    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 8, y1), color, -1)
                    cv2.putText(frame, text, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            # Status overlay
            if YOLO_AVAILABLE:
                status = f"YOLO {yolo_model_size.upper()} | {yolo_fps:.1f} FPS | {yolo_inference_ms:.0f}ms | conf>{yolo_confidence:.0%}"
                if yolo_preprocess:
                    status += " | CLAHE"
            else:
                status = "YOLO: NOT INSTALLED"

            # Achtergrond voor status
            cv2.rectangle(frame, (5, 5), (450, 30), (0, 0, 0), -1)
            cv2.putText(frame, status, (10, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            sleep(0.04)  # ~25 FPS stream

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
            padding: 15px;
            min-height: 100vh;
        }
        h1 { color: #00d4ff; margin-bottom: 8px; font-size: 1.4em; }
        .container {
            display: flex;
            gap: 15px;
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
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #00d4ff;
            width: 300px;
        }
        .section {
            background: #0f0f23;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .section-title {
            color: #00d4ff;
            font-size: 11px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .meter { margin: 4px 0; }
        .meter-label { font-size: 12px; }
        .meter-bar {
            background: #333;
            height: 16px;
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
            grid-template-columns: repeat(3, 40px);
            gap: 3px;
            justify-content: center;
        }
        .key {
            background: #333;
            border: 2px solid #555;
            border-radius: 4px;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            font-size: 13px;
            transition: all 0.1s;
        }
        .key.active { background: #00d4ff; color: #000; border-color: #00d4ff; }
        .key.empty { visibility: hidden; }
        .cam-grid {
            display: grid;
            grid-template-columns: repeat(3, 36px);
            gap: 2px;
            justify-content: center;
        }
        .cam-btn {
            background: #333;
            border: 2px solid #555;
            border-radius: 4px;
            padding: 5px;
            color: #eee;
            font-family: monospace;
            font-size: 11px;
            cursor: pointer;
        }
        .cam-btn:hover { border-color: #00d4ff; }
        .cam-btn:active { background: #00d4ff; color: #000; }
        .btn-row {
            display: flex;
            gap: 5px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            padding: 6px 10px;
            border: 2px solid #555;
            border-radius: 4px;
            background: #333;
            color: #eee;
            font-family: monospace;
            font-size: 10px;
            cursor: pointer;
        }
        .btn:hover { border-color: #00d4ff; }
        .btn.active { background: #00d4ff; color: #000; border-color: #00d4ff; }
        .btn.night.active { background: #6b5bff; border-color: #6b5bff; }
        .btn.yolo.active { background: #44ff44; border-color: #44ff44; color: #000; }
        .btn.model { min-width: 60px; font-size: 9px; }
        .btn.model.v11.active { background: #44ff88; border-color: #44ff88; color: #000; }
        .btn.model.v8.active { background: #ff8844; border-color: #ff8844; color: #000; }
        .slider-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }
        .slider-row label { font-size: 10px; color: #888; min-width: 70px; }
        .slider-row input[type="range"] { flex: 1; }
        .slider-row span { font-size: 11px; min-width: 35px; color: #00d4ff; }
        .detect-list {
            max-height: 100px;
            overflow-y: auto;
            font-size: 10px;
            margin-top: 8px;
        }
        .detect-item {
            padding: 2px 0;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
        }
        .detect-label { color: #44ff44; }
        .detect-conf { color: #888; }
        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            margin-top: 5px;
        }
        .info-row span:first-child { color: #888; }
        .info-row span:last-child { color: #00d4ff; }
    </style>
</head>
<body>
    <h1>PiCar-X + YOLO (Pi 5)</h1>
    <div class="container">
        <div class="video-box">
            <img id="stream" src="/video_feed" alt="Camera Stream">
        </div>
        <div class="controls">
            <!-- Driving -->
            <div class="section">
                <div class="section-title">Driving (WASD)</div>
                <div class="meter">
                    <div class="meter-label">Speed: <span id="speed-val">0</span></div>
                    <div class="meter-bar">
                        <div class="meter-fill" id="speed-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="meter">
                    <div class="meter-label">Steer: <span id="steer-val">0</span>°</div>
                    <div class="meter-bar" style="position: relative;">
                        <div style="position:absolute;left:50%;width:2px;height:100%;background:#fff"></div>
                        <div class="meter-fill" id="steer-bar" style="width: 4px; margin-left: 50%;"></div>
                    </div>
                </div>
                <div style="margin-top:8px;">
                    <div class="keys">
                        <div class="key empty"></div>
                        <div class="key" id="key-w">W</div>
                        <div class="key empty"></div>
                        <div class="key" id="key-a">A</div>
                        <div class="key" id="key-s">S</div>
                        <div class="key" id="key-d">D</div>
                    </div>
                </div>
            </div>

            <!-- Camera -->
            <div class="section">
                <div class="section-title">Camera (IJKL)</div>
                <div class="cam-grid">
                    <div class="key empty"></div>
                    <button class="cam-btn" onclick="camTilt(5)">Up</button>
                    <div class="key empty"></div>
                    <button class="cam-btn" onclick="camPan(-5)">L</button>
                    <button class="cam-btn" onclick="camCenter()">C</button>
                    <button class="cam-btn" onclick="camPan(5)">R</button>
                    <div class="key empty"></div>
                    <button class="cam-btn" onclick="camTilt(-5)">Dn</button>
                    <div class="key empty"></div>
                </div>
                <div class="info-row">
                    <span>Pan/Tilt:</span>
                    <span><span id="pan-val">0</span>° / <span id="tilt-val">0</span>°</span>
                </div>
                <div class="btn-row" style="margin-top:8px;">
                    <button class="btn night" id="btn-night" onclick="setMode('night')">Night</button>
                    <button class="btn day" id="btn-day" onclick="setMode('day')">Day</button>
                </div>
            </div>

            <!-- YOLO Settings -->
            <div class="section">
                <div class="section-title">YOLO Detection</div>
                <div class="btn-row">
                    <button class="btn yolo" id="btn-yolo" onclick="toggleYolo()">YOLO ON</button>
                    <button class="btn" id="btn-clahe" onclick="toggleClahe()">CLAHE ON</button>
                </div>
                <div style="margin-top:8px;font-size:9px;color:#888;text-align:center;">YOLOv11 (aanbevolen)</div>
                <div class="btn-row" style="margin-top:4px;">
                    <button class="btn model v11" id="btn-v11-nano" onclick="setModel('v11-nano')">v11 Nano</button>
                    <button class="btn model v11" id="btn-v11-small" onclick="setModel('v11-small')">v11 Small</button>
                    <button class="btn model v11" id="btn-v11-medium" onclick="setModel('v11-medium')">v11 Med</button>
                </div>
                <div style="margin-top:6px;font-size:9px;color:#666;text-align:center;">YOLOv8 (ouder)</div>
                <div class="btn-row" style="margin-top:4px;">
                    <button class="btn model v8" id="btn-v8-nano" onclick="setModel('v8-nano')">v8 Nano</button>
                    <button class="btn model v8" id="btn-v8-small" onclick="setModel('v8-small')">v8 Small</button>
                    <button class="btn model v8" id="btn-v8-medium" onclick="setModel('v8-medium')">v8 Med</button>
                </div>
                <div class="slider-row">
                    <label>Confidence:</label>
                    <input type="range" id="conf-slider" min="10" max="80" value="35" oninput="setConfidence(this.value)">
                    <span id="conf-val">35%</span>
                </div>
                <div class="info-row">
                    <span>Model:</span>
                    <span id="current-model">v11-small</span>
                </div>
                <div class="info-row">
                    <span>Performance:</span>
                    <span><span id="yolo-fps">0</span> FPS / <span id="yolo-ms">0</span>ms</span>
                </div>
                <div class="detect-list" id="detect-list">
                    <div style="color:#888">Waiting...</div>
                </div>
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

        function toggleClahe() {
            fetch('/yolo/clahe', {method: 'POST'});
        }

        function setModel(size) {
            fetch('/yolo/model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({size: size})
            });
        }

        function setConfidence(val) {
            document.getElementById('conf-val').textContent = val + '%';
            fetch('/yolo/confidence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({confidence: val / 100})
            });
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

            const claheBtn = document.getElementById('btn-clahe');
            claheBtn.classList.toggle('active', data.yolo_preprocess);
            claheBtn.textContent = data.yolo_preprocess ? 'CLAHE ON' : 'CLAHE OFF';

            // Update model buttons
            const models = ['v11-nano', 'v11-small', 'v11-medium', 'v8-nano', 'v8-small', 'v8-medium'];
            models.forEach(m => {
                const btn = document.getElementById('btn-' + m);
                if (btn) btn.classList.toggle('active', data.yolo_model === m);
            });
            document.getElementById('current-model').textContent = data.yolo_model;

            document.getElementById('yolo-fps').textContent = data.yolo_fps.toFixed(1);
            document.getElementById('yolo-ms').textContent = data.yolo_ms.toFixed(0);

            const list = document.getElementById('detect-list');
            if (data.detections.length === 0) {
                list.innerHTML = '<div style="color:#888">No objects detected</div>';
            } else {
                list.innerHTML = data.detections.slice(0, 10).map(d =>
                    `<div class="detect-item"><span class="detect-label">${d.label}</span><span class="detect-conf">${(d.confidence * 100).toFixed(0)}%</span></div>`
                ).join('');
            }
        }, 200);

        // Init
        document.getElementById('btn-night').classList.add('active');
        document.getElementById('btn-yolo').classList.add('active');
        document.getElementById('btn-clahe').classList.add('active');
        document.getElementById('btn-v11-small').classList.add('active');
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/video_feed')
def video_feed():
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
        'yolo_ms': yolo_inference_ms,
        'yolo_model': yolo_model_size,
        'yolo_preprocess': yolo_preprocess,
        'yolo_confidence': yolo_confidence,
        'detections': detections
    })


@app.route('/yolo/toggle', methods=['POST'])
def toggle_yolo():
    global yolo_enabled
    yolo_enabled = not yolo_enabled
    return jsonify({'ok': True, 'enabled': yolo_enabled})


@app.route('/yolo/clahe', methods=['POST'])
def toggle_clahe():
    global yolo_preprocess
    yolo_preprocess = not yolo_preprocess
    return jsonify({'ok': True, 'enabled': yolo_preprocess})


@app.route('/yolo/confidence', methods=['POST'])
def set_confidence():
    global yolo_confidence
    data = request.json
    yolo_confidence = max(0.1, min(0.9, data.get('confidence', 0.35)))
    return jsonify({'ok': True, 'confidence': yolo_confidence})


@app.route('/yolo/model', methods=['POST'])
def change_model():
    global yolo_model, yolo_model_size, current_model_name

    if not YOLO_AVAILABLE:
        return jsonify({'ok': False, 'error': 'YOLO not available'})

    data = request.json
    size = data.get('size', 'small')

    if size not in AVAILABLE_MODELS:
        return jsonify({'ok': False, 'error': 'Invalid model size'})

    try:
        model_file = AVAILABLE_MODELS[size]
        print(f"Loading model: {model_file}")
        from ultralytics import YOLO
        yolo_model = YOLO(model_file)
        yolo_model_size = size
        current_model_name = model_file
        print(f"Model {size} loaded!")
        return jsonify({'ok': True, 'model': size})
    except Exception as e:
        print(f"Model load error: {e}")
        return jsonify({'ok': False, 'error': str(e)})


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
    print("Starting camera...")
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=False)
    sleep(2)

    apply_camera_preset(NIGHT_MODE)

    physics_thread = Thread(target=physics_loop, daemon=True)
    physics_thread.start()

    if YOLO_AVAILABLE:
        yolo_thread = Thread(target=yolo_detection_loop, daemon=True)
        yolo_thread.start()
        print("YOLO detection thread started")

    ip = get_ip()
    print(f"\n" + "="*50)
    print(f"  Open in browser: http://{ip}:5000")
    print(f"  YOLO: {'ENABLED' if YOLO_AVAILABLE else 'NOT INSTALLED'}")
    print(f"  Model: {current_model_name}")
    print(f"="*50 + "\n")

    try:
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
    finally:
        px.stop()
        Vilib.camera_close()
