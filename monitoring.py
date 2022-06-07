from db_connection import *
import cv2
from tensorflow.keras.models import load_model
import numpy as np
from pygame import mixer
from datetime import datetime
import time

#Monitoring
def monitoring(nama,stambuk, matkul):
    start_time = datetime.now()
    start_time = start_time.strftime("%D:%H:%M:%S")

    face_cascade = cv2.CascadeClassifier('C:\\Users\\My ASUS\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('C:\\Users\\My ASUS\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\cv2\\data\\haarcascade_eye.xml')

    model = load_model("modelcnn.h5")
    mixer.init()
    sound = mixer.Sound('alarm.wav')
    cap = cv2.VideoCapture(1)
    Score = 0
    Score2 = 0
    Score3 = 0
    Sec = 0

    while True:
        Sec = Sec+1
        ret, frame = cap.read()
        height, width = frame.shape[0:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7)
        cv2.rectangle(frame, (0, 50), (100, 0), (0, 0, 0), thickness=cv2.FILLED)
        cv2.putText(frame, str(Sec), (10, 20),
                    fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                    color=(50, 255, 50),
                    thickness=1, lineType=cv2.LINE_AA)

        if isinstance(eyes, tuple):
            cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)
            cv2.putText(frame, 'Tidak Aktif', (10, height - 20), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                        color=(50, 50, 255),
                        thickness=1, lineType=cv2.LINE_AA)
            Score2 = Score2 + 1
            time.sleep(1)
            if Score2 > 5:
                sound.play()
                if Score2 > 10:
                    Score3 = Score3 + 1
                    cv2.rectangle(frame, (0, height - 50), (300, height), (0, 0, 0), thickness=cv2.FILLED)
                    cv2.putText(frame, 'Tidak Aktif : ' + str(Score3) + ' detik', (10, height - 20),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                                color=(50, 50, 255),
                                thickness=1, lineType=cv2.LINE_AA)
            else:
                sound.stop()
        else:
            Score2 = 0

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(255, 50, 50), thickness=3)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, pt1=(ex, ey), pt2=(ex + ew, ey + eh), color=(50, 255, 50), thickness=2)

            # preprocessing steps
            eye = frame[ey:ey + eh, ex:ex + ew]
            eye = cv2.resize(eye, (80, 80))
            eye = eye / 255
            eye = eye.reshape(80, 80, 3)
            eye = np.expand_dims(eye, axis=0)
            # preprocessing is done now model prediction
            prediction = model.predict(eye)
            # if eyes are closed
            if prediction[0] < 0.90:
                cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)
                cv2.putText(frame, 'Tidak Aktif', (10, height - 20), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            fontScale=1,
                            color=(50, 50, 255),
                            thickness=1, lineType=cv2.LINE_AA)
                Score = Score + 1
                time.sleep(1)
                if (Score > 5):
                    sound.play()
                    if Score > 10:
                        Score3 = Score3 + 1
                        cv2.rectangle(frame, (0, height - 50), (300, height), (0, 0, 0), thickness=cv2.FILLED)
                        cv2.putText(frame, 'Tidak Aktif : ' + str(Score3) + ' detik', (10, height - 20),
                                    fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                                    color=(50, 50, 255),
                                    thickness=1, lineType=cv2.LINE_AA)
                else:
                    sound.stop()
                # print("|",Sec,"|\tNilai Prediksi = ", prediction, "\tHasil Prediksi = Tidak Aktif \tKeterangan = Mata Terdeteksi", "\t\tWaktu Tidak Aktif = ", Score3)
            # if eyes are open
            elif prediction[0] > 0.90:
                cv2.rectangle(frame, (0, height - 50), (100, height), (0, 0, 0), thickness=cv2.FILLED)
                cv2.putText(frame, 'Aktif', (10, height - 20), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                            color=(50, 255, 50),
                            thickness=1, lineType=cv2.LINE_AA)
                Score = 0
                time.sleep(1)
                # print("|",Sec,"|\tNilai Prediksi = ", prediction, "\tHasil Prediksi = Aktif \t\t\tKeterangan = Mata Terdeteksi", "\t\tWaktu Tidak Aktif = ", Score3)
        cv2.imshow('Sistem Monitoring Mahasiswa', frame)
        if cv2.waitKey(33) & 0xFF == ord('q'):
            end_time = datetime.now()
            end_time = end_time.strftime("%D:%H:%M:%S")
            insertrec = db.cursor()
            sqlquery = "INSERT INTO " + str(matkul) +\
                       "(Nama, Stambuk, Mata_Kuliah, Waktu_Masuk, Waktu_Keluar, Waktu_Tidak_Fokus_Detik) " \
                       "VALUES(%s, %s, %s, %s, %s, %s)"
            value = (nama, stambuk, matkul, start_time, end_time, Score3)
            insertrec.execute(sqlquery, value)
            db.commit()
            print("===================================================================================================================================")
            print("                                                      HASIL MONITORING                                                             ")
            print("===================================================================================================================================")
            print("Nama :", nama, "\t\tNIM :", stambuk,"\tWaktu Masuk :", start_time, "\tWaktu Keluar :", end_time, "Waktu Tidak Fokus :", Score3, "detik")
            print("Sukses mengirim hasil monitoring ke database !!!")
            break

    cap.release()
    cv2.destroyAllWindows()