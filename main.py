import cv2 as handler
import imutils
import threading
from datetime import datetime
import winsound
from twilio.rest import Client
import time
import keys

cap = handler.VideoCapture(0, handler.CAP_DSHOW)

cap.set(handler.CAP_PROP_FRAME_WIDTH, 640)
cap.set(handler.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = handler.cvtColor(start_frame, handler.COLOR_BGR2GRAY)
start_frame = handler.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0


def beep_alarm():
    global alarm
    for _ in range(5):
        if not alarm_mode:
            break
        winsound.Beep(440, 1000)
    alarm = False


while True:
    timestamp = datetime.now()
    _, frame = cap.read()
    frame = imutils.resize(frame, width=500)

    if alarm_mode:
        frame_bw = handler.cvtColor(frame, handler.COLOR_BGR2GRAY)
        frame_bw = handler.GaussianBlur(frame_bw, (5, 5), 0)

        difference = handler.absdiff(frame_bw, start_frame)
        threshold = handler.threshold(difference, 25, 255, handler.THRESH_BINARY)[1]
        start_frame = frame_bw

        print(f' {timestamp} | changes {threshold.sum()}')
        print(f' {timestamp} | Intensity {alarm_counter*2}%')
        if threshold.sum() > 100000:
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1

        handler.imshow("Cam", threshold)
    else:
        handler.imshow("Cam", frame)

    if alarm_counter > 50:
        if not alarm:
            alarm = True
            threading.Thread(target=beep_alarm).start()
            client = Client(keys.account_sid, keys.auth_token)
            message = client.messages.create(body=f'Alert, motion detected {timestamp}', from_=keys.twilio_number,
                                             to=keys.target_number)

            print(f'ALERT TYPE : [Motion detected]  at {timestamp } sent')
            time.sleep(5)
            alarm_counter = 0

    key_pressed = handler.waitKey(30)
    if key_pressed == ord('t'):
        alarm_mode = not alarm_mode
        alarm_counter = 0

    if key_pressed == ord('q'):
        alarm_mode = False
        break


cap.release()
handler.destroyAllWindows()
