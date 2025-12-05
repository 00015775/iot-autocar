# Web App (Edge & Cloud)
---
## Flask

Flask for the backend, basic HTML/CSS/JS for the frontend, and Flask-SocketIO for real-time updates and communication (such as, sensor reading and control of actuators). 

`Flask` → Web server
`Flask-SocketIO` → Real-time communication
`eventlet` → Required for SocketIO
`RPi.GPIO` or `gpiozero` → Control GPIO pins on Pi

### Run these commands on Pi:
```shell
sudo apt update && sudo apt upgrade
```
```shell
pip install flask flask-socketio eventlet RPi.GPIO
```
When the `app.py` is ready then run:
```shell
python app.py
```
<pre>
iot-autocar-web/
│
├── app.py                 # Flask + SocketIO server; Integrates existing logic
│
├── templates/
│   └── index.html         # Web interface (HTML/CSS/JS) for UI
│
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Frontend JS for real-time updates
│
├── car_control.py         # Python functions to drive motors, servo, read sensors
│
└── sensor_reader.py       # Read IR and Ultrasonic sensor values
</pre>

---

## Streamlit

Streamlit offers a very easy way to create interactive dashboards.Can handle sliders, buttons, live charts, and indicators without HTML/JS. Python-only — no need to write separate JS or use SocketIO. Quick deployment to cloud (e.g., Streamlit Community Cloud, free tier) with a single `git push`.

### Run these commands on Pi:
```shell
sudo apt update && sudo apt upgrade
```
```shell
pip install streamlit
```
When the `app.py` is ready then run:
```shell
streamlit run app.py
```
<pre>
iot-autocar-web/
│
├── app.py                 # Main Streamlit app
├── car_control.py         # Motor and servo control functions
├── sensor_reader.py       # Read IR, ultrasonic, servo angle
├── requirements.txt       # For cloud deployment
├── assets/                # Images, icons
│   └── car.png
└── utils.py               # Optional helpers (e.g., joystick parsing, PWM handling)
</pre>

