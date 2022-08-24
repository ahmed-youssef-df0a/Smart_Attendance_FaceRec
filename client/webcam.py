# import the opencv library

import cv2
import redis
import time

r = redis.Redis(host='localhost', port=7777, db=0)

print("Starting...")

vid = cv2.VideoCapture(-1)
def cam(vid):
        ret, frame = vid.read()
        ret, img = cv2.imencode('.png', frame)
        frame = img.tobytes()
        r.set('frame', frame)
    
while True:
    time.sleep(0.08)
    if r.get('action') == b'1':
        cam(vid)
    if r.get('action') == b'0':
        r.delete('action')
        exit()
    if r.get('action') == b'2':
        continue


    


    