import cv2
import RPi.GPIO as GPIO
import time
import subprocess
import os
from datetime import datetime
BUTTON_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None
recording = False
record_process  = None
last_button_state= GPIO.LOW
def find_usb_path():
    base_path = '/media/xulixuan/'
    if os.path.exists(base_path):
        devices = os.listdir(base_path)
        if devices:
            return os.path.join(base_path, devices[0])
    return None
print("等待按键控制录像开始/停止...")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("摄像头读取失败")
            break
           
        cv2.imshow('Camera Preview', frame)
        current_button_state=GPIO.input(BUTTON_GPIO)
        if GPIO.input(BUTTON_GPIO) == GPIO.HIGH and last_button_state == GPIO.LOW:
            if not recording:
                usb_mount_path = find_usb_path()
                if usb_mount_path:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = os.path.join(usb_mount_path, f"record_{timestamp}.avi")
                    print(f"开始录像，保存至：{filename }")
                    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
                    recording = True
                else:
                    print("未找到U盘，无法开始录像")
       
        if GPIO.input(BUTTON_GPIO) == GPIO.LOW and last_button_state == GPIO.HIGH:
                print("停止录像")
                recording = False
                if out:
                    out.release()
                    out = None
                    time.sleep(0.5) # 消抖
        last_button_state=current_button_state
        if recording and out is not None:
            out.write(frame)
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
       
        time.sleep(0.01)
         
except KeyboardInterrupt:
    print("程序被终止")

finally:
    if recording and out is not None:
        out.release()
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()