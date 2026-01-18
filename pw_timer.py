import sys
import time
import threading
from flask import Flask
from flask_cors import CORS
from PyQt5 import QtWidgets, QtCore, QtGui

# ========= Flask Setup =========
app = Flask(__name__)
CORS(app)

start_time = None
total_time = 0
running = False

@app.route("/start", methods=["POST"])
def start():
    global start_time, running
    if not running:
        start_time = time.time()
        running = True
    return "started"

@app.route("/stop", methods=["POST"])
def stop():
    global start_time, total_time, running
    if running:
        total_time += time.time() - start_time
        running = False
    return "stopped"

@app.route("/manual-start", methods=["POST"])
def manual_start():
    return start()

@app.route("/manual-stop", methods=["POST"])
def manual_stop():
    return stop()

def run_flask():
    app.run(port=5000)

# ========= PyQt5 GUI =========
class FloatingTimer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Frameless & always-on-top
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.Tool
        )
        self.setFixedSize(250, 120)
        self.setStyleSheet("""
            background-color: #2C3E50;  /* Dark blue background */
            border-radius: 15px;
        """)

        # Draggable variables
        self.offset = None

        # Timer label
        self.label = QtWidgets.QLabel("00:00:00", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setGeometry(10, 10, 230, 50)
        font = QtGui.QFont("Helvetica", 28, QtGui.QFont.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #FF4500;")  # Orange text

        # Start/Stop buttons
        self.start_btn = QtWidgets.QPushButton("Start", self)
        self.start_btn.setGeometry(30, 70, 80, 35)
        self.start_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 8px;"
        )
        self.start_btn.clicked.connect(self.manual_start)

        self.stop_btn = QtWidgets.QPushButton("Stop", self)
        self.stop_btn.setGeometry(140, 70, 80, 35)
        self.stop_btn.setStyleSheet(
            "background-color: #F44336; color: white; border-radius: 8px;"
        )
        self.stop_btn.clicked.connect(self.manual_stop)

        # Timer update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def manual_start(self):
        global start_time, running
        if not running:
            start_time = time.time()
            running = True

    def manual_stop(self):
        global start_time, total_time, running
        if running:
            total_time += time.time() - start_time
            running = False

    def update_timer(self):
        global start_time, total_time, running
        if running:
            elapsed = time.time() - start_time + total_time
        else:
            elapsed = total_time
        mins, secs = divmod(int(elapsed), 60)
        hours, mins = divmod(mins, 60)
        self.label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")

    # Dragging window
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x - x_w, y - y_w)

    def mouseReleaseEvent(self, event):
        self.offset = None

# ========= Main =========
if __name__ == "__main__":
    # Start Flask server
    threading.Thread(target=run_flask, daemon=True).start()

    # Start PyQt5 GUI
    app_qt = QtWidgets.QApplication(sys.argv)
    window = FloatingTimer()
    window.show()
    sys.exit(app_qt.exec_())
