import cv2
import face_recognition

# تحميل الصور من نموذج التدريب
known_image = face_recognition.load_image_file("path/to/known_person.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# تشغيل كاميرا الجهاز
cap = cv2.VideoCapture(0)

while True:
    # قراءة الإطار من كاميرا الجهاز
    ret, frame = cap.read()

    # تحويل الإطار إلى تشفير للتعرف على الوجوه
    unknown_encoding = face_recognition.face_encodings(frame)

    if unknown_encoding:
        # يوجد وجه في الإطار
        result = face_recognition.compare_faces([known_encoding], unknown_encoding[0])

        if result[0]:
            print("تم التعرف على الشخص.")
            # هنا يمكنك فتح شاشة البرنامج الرئيسية
        else:
            print("لا توجد تطابق في الصورة.")
            # هنا يمكنك إظهار إشعار بأنه لا يوجد تطابق

    # عرض الإطار
    cv2.imshow("Camera", frame)

    # انتظار الضغط على مفتاح لإنهاء البرنامج
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# إيقاف تشغيل كاميرا الجهاز وإغلاق النوافذ
cap.release()
cv2.destroyAllWindows()
