import cv2
import requests
import threading
from flask import Flask, Response

app = Flask(__name__)

# Load OpenCV's built-in Face Detector AI
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Helper function to send triggers without freezing the video stream
def send_trigger(action_name):
    try:
        requests.post("http://localhost:3000/api/trigger", json={"action": action_name}, timeout=1)
        print(f">> Sent '{action_name}' signal to dashboard!")
    except:
        pass

def generate_frames():
    cap = cv2.VideoCapture(0)
    success, frame1 = cap.read()
    success, frame2 = cap.read()

    approach_triggered = False
    taken_triggered = False

    while cap.isOpened():
        # 1. Get Motion
        diff = cv2.absdiff(frame1, frame2)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray_diff, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 2. Find Face
        gray_frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

        status = "IDLE (Waiting for pill...)"
        color = (0, 255, 0)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame1, "Patient Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Trigger Approach
            if not approach_triggered:
                threading.Thread(target=send_trigger, args=("approach",)).start()
                approach_triggered = True

            # 3. Eating Zone
            mz_x = x - 20
            mz_y = y + int(h * 0.6)
            mz_w = w + 40
            mz_h = int(h * 0.6)

            cv2.rectangle(frame1, (mz_x, mz_y), (mz_x+mz_w, mz_y+mz_h), (0, 255, 255), 2)
            cv2.putText(frame1, "Eating Zone", (mz_x, mz_y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # 4. Check Motion inside Eating Zone
            for contour in contours:
                if cv2.contourArea(contour) < 1500:
                    continue
                    
                cx, cy, cw, ch = cv2.boundingRect(contour)
                motion_center_y = cy + ch // 2
                motion_center_x = cx + cw // 2

                if mz_x < motion_center_x < (mz_x + mz_w) and mz_y < motion_center_y < (mz_y + mz_h):
                    status = "EATING PILL VERIFIED!"
                    color = (0, 0, 255)
                    cv2.rectangle(frame1, (cx, cy), (cx+cw, cy+ch), (0, 0, 255), 3)

                    # Trigger Taken
                    if not taken_triggered:
                        threading.Thread(target=send_trigger, args=("taken",)).start()
                        taken_triggered = True

        cv2.putText(frame1, f"Status: {status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 4)
        
        # --- THIS IS THE MAGIC: Convert frame to jpeg and stream it ---
        ret, buffer = cv2.imencode('.jpg', frame1)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Setup for next frame
        frame1 = frame2
        success, frame2 = cap.read()

# Route to view the video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("🚀 AI Video Server running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)