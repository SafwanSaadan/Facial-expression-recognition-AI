import cv2  # استيراد مكتبة OpenCV لمعالجة الصور
import mediapipe as mp  # استيراد مكتبة mediapipe التي تقدم حلاً للتعرف على الوجوه والمزيد
import time  # استيراد مكتبة time للتحكم في الوقت

# تعريف فئة FaceMeshDetector
class FaceMeshDetector():

    def __init__(self, staticMode=False, maxFaces=2, minDetectionCon=0.5, minTrackCon=0.5):
        # المُعمل مع المتغيرات والإعدادات عند إنشاء كائن من هذه الفئة
        self.staticMode = staticMode  # وضع ثابت للكشف
        self.maxFaces = maxFaces  # عدد الوجوه الذي يتعرف عليها البرنامج
        self.minDetectionCon = minDetectionCon  # الحد الأدنى لثقة الكشف
        self.minTrackCon = minTrackCon  # الحد الأدنى لثقة التتبع

        # استخدام مكتبة mediapipe لرسم الوجه على الصورة
        self.mpDraw = mp.solutions.drawing_utils
        # استخدام مكتبة mediapipe للكشف عن الوجه
        self.mpFaceMesh = mp.solutions.face_mesh
        # إنشاء كائن FaceMesh باستخدام الإعدادات المحددة
        self.faceMesh = self.mpFaceMesh.FaceMesh(static_image_mode=self.staticMode, max_num_faces=self.maxFaces, min_detection_confidence=self.minDetectionCon, min_tracking_confidence=self.minTrackCon)
        # إعدادات لرسم الوجه
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=2)

    # دالة للبحث عن الوجوه في الصورة
    def findFaceMesh(self, img, draw=True):
        # تحويل الصورة إلى تنسيق RGB
        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # معالجة الصورة باستخدام كائن FaceMesh
        self.results = self.faceMesh.process(self.imgRGB)
        faces = []
        if self.results.multi_face_landmarks:
            for faceLms in self.results.multi_face_landmarks:
                if draw:
                    # رسم نقاط الوجه على الصورة
                    self.mpDraw.draw_landmarks(img, faceLms, self.mpFaceMesh.FACEMESH_TESSELATION,
                                        self.drawSpec, self.drawSpec)
                face = []
                for id, lm in enumerate(faceLms.landmark):
                    ih, iw, ic = img.shape
                    x, y = int(lm.x * iw), int(lm.y * ih)
                    face.append([x, y])
                faces.append(face)
        return img, faces

# دالة رئيسية لتنفيذ البرنامج
def main():
    # فتح ملف الفيديو
    cap = cv2.VideoCapture("Videos/1.mp4")
    pTime = 0
    # إنشاء كائن FaceMeshDetector
    detector = FaceMeshDetector(maxFaces=2)
    while True:
        # قراءة الإطار الحالي من ملف الفيديو
        success, img = cap.read()
        # استخدام كائن FaceMeshDetector للبحث عن الوجوه
        img, faces = detector.findFaceMesh(img)
        if len(faces)!= 0:
            # طباعة إحدى الوجوه (نقاط الوجه)
            print(faces[0])
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        # عرض معدل الإطارات في الصورة
        cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 255, 0), 3)
        # عرض الصورة
        cv2.imshow("Image", img)
        # انتظار للمفتاح لمدة 1 مللي ثانية (لعرض الإطار التالي)
        cv2.waitKey(1)

# تنفيذ الدالة الرئيسية عند تشغيل البرنامج
if __name__ == "__main__":
    main()
