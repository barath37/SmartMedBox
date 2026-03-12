from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# This variable remembers if the ESP32 detected a patient
sensor_triggered = False

# We put the HTML directly inside the Python file to keep it simple!
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Med Box Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background-color: #eef2f3;}
        #video-container { display: none; margin-top: 20px; border: 5px solid #ff4d4d; border-radius: 10px; padding: 10px; background: white; display: inline-block;}
        #log { margin-top: 30px; text-align: left; display: inline-block; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); width: 400px;}
        .status-idle { color: #555; }
        .status-alert { color: #ff4d4d; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🏥 Caregiver Dashboard</h1>
    <h2 id="status-text" class="status-idle">Status: Waiting for Patient...</h2>

    <div id="video-container" style="display: none;">
        <h3 style="color: red; margin-top: 0;">🔴 Patient Detected - Live Verification</h3>
        <video id="alert-video" width="400" controls muted>
            <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
        </video>
    </div>

    <div id="log">
        <h3>📋 Progress Log:</h3>
        <ul id="log-list">
            <li><i>System initialized and monitoring...</i></li>
        </ul>
    </div>

    <script>
        // This JavaScript asks the Python server for updates every 2 seconds
        setInterval(function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.triggered) {
                        // Change text
                        document.getElementById('status-text').innerText = "Status: Patient at Dispenser!";
                        document.getElementById('status-text').className = "status-alert";
                        
                        // Show and play video
                        document.getElementById('video-container').style.display = "inline-block";
                        document.getElementById('alert-video').play();
                        
                        // Add to log (only if we haven't added it yet)
                        let logList = document.getElementById('log-list');
                        if (logList.innerHTML.indexOf("Patient approached") === -1) {
                            let time = new Date().toLocaleTimeString();
                            logList.innerHTML += "<li><b>" + time + "</b> - Patient approached box. Video verification started.</li>";
                        }
                    }
                });
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Show the dashboard website
    return render_template_string(HTML_PAGE)

@app.route('/trigger')
def trigger():
    # The ESP32 will visit this URL when the PIR sensor fires
    global sensor_triggered
    sensor_triggered = True
    return "SUCCESS: Alarm triggered on dashboard!"

@app.route('/status')
def status():
    # The website constantly checks this URL
    return jsonify({"triggered": sensor_triggered})

@app.route('/reset')
def reset():
    # Visit this URL to reset the dashboard for the next test
    global sensor_triggered
    sensor_triggered = False
    return "Dashboard reset to Idle state."

if __name__ == '__main__':
    # Run the server on your local Wi-Fi network
    app.run(host='0.0.0.0', port=5000)