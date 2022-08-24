import datetime , time
import face_recognition
import cv2
import numpy as np
from flask_app import red , db
from flask_app.models import Student , Attendance_Log , Course 


def get_encode():
    try:
        img=red.get('frame')
        while img is None:
            img=red.get('frame')
        if img:
            frame = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
            
        
            
                    
        try:
            img_face_locations = face_recognition.face_locations(frame)
            img_face_encoding = face_recognition.face_encodings(frame, img_face_locations)[0]
        except IndexError:
            return None
        # check if img_face_encoding is empty

        with open("temp.txt", "w") as w:
            for i in img_face_encoding:
                w.write(str(i) +"\n")
            w.close()
        with open("temp.txt", "r") as r:        
            data = r.read()
            r.close()
        with open("temp.txt", "r+") as d:
            d.truncate(0)
            d.close()
        return data
    except Exception:
        return None


def wcam(): 
    while True:
        time.sleep(0.1)
        img_bytes = red.get('frame')
        if img_bytes:
            yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n\r\n')


def face_detect(course_id):
        course = Course.query.filter_by(course_id=course_id).first()
        if course:
            students = course.takers
        if students is None:
            return None
        known_face_encodings = []
        known_face_names = []
        checked_faces=['']
        print("[INFO] loading encodings...")
        for user in students:
            known_face_names.append(user.name)
            a = open("temp.txt", "a")
            a.write(user.face_encode)
            encodel =[]
            a.close()
            with open("temp.txt", "r+") as r:
                lines = r.readlines()
                r.seek(0)
                r.writelines(line for line in lines if line.strip())
                r.truncate()
                r.close()
            with open("temp.txt", "r") as f:
                for i in f:
                    encodel.append(float(i.strip()))
                f.close()
            with open("temp.txt", "r+") as d:
                d.truncate(0)
                d.close()

            known_face_encodings.append(encodel)
        
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        print("[OK] encodings...")



        while True:
                time.sleep(0.1)
                img_bytes = red.get('frame')
                if img_bytes:
                    frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                    red.delete('frame')
                else:
                    continue

                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = small_frame[:, :, ::-1]

                if process_this_frame:
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding , tolerance=0.4)
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame


                
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    if name == "Unknown":
                        clr = (0, 0, 255)
                    else:
                        clr = (0, 255, 0)
                        if name not in checked_faces:
                                #check in the database if the name is attended today
                                today = datetime.datetime.now().date()
                                #get time 12 hour format
                                now = datetime.datetime.now().strftime("%I:%M:%S %p")
                                student_id = Student.query.filter_by(name=name).first().student_id
                                
                                if Attendance_Log.query.filter_by(name=name, date=today ,course_id=course_id ).first():
                                    pass
                                else:
                                    attendance_log = Attendance_Log(student_id=student_id, name=name, course_id=course_id,date=today, time=now)
                                    db.session.add(attendance_log)
                                    db.session.commit()
                                    checked_faces.append(name)
                    cv2.rectangle(frame, (left, top), (right, bottom), clr, 2 )

                    
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), clr, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)
                ret ,buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')