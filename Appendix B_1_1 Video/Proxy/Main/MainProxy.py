import socket
from flask import Flask, Response
import cv2
import datetime

from ..CommandsForCAPIF.PythonFiles import AuthenticationAndAuthorization as aaa

app = Flask(__name__)


def generate_frames():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 5001)
    client_socket.connect(server_address)

    camera = cv2.VideoCapture(3)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    previous_resolution = None
    resolution = None

    last_time = datetime.datetime.now()
    last_time_fps = datetime.datetime.now()

    width = 1280
    height = 720
    fps = 30.0

    while True:
        time_to_sleep = 5.0 - (datetime.datetime.now() - last_time).total_seconds()

        if time_to_sleep <= 0:
            data = client_socket.recv(13)

            if data:
                resolution = data.decode()
                resolution = resolution.replace("E", "")

                width, height, fps = map(int, resolution.split('x'))
                last_time = datetime.datetime.now()

        if resolution and resolution != previous_resolution:
            previous_resolution = resolution

            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            camera.set(cv2.CAP_PROP_FPS, fps)

        success, frame = camera.read()

        if not success:
            break
        else:
            time_to_sleep_fps = (datetime.datetime.now() - last_time_fps).total_seconds()
            actual_hertz_time = (1.0 / fps)

            if actual_hertz_time <= time_to_sleep_fps:
                last_time_fps = datetime.datetime.now()

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    client_socket.close()


@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    
    aaa.all_commands()
    app.run(host='127.0.0.1', port=5000, debug=True)
    