import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from keras.models import load_model
import numpy as np
import threading
from googletrans import Translator
import pyttsx3
from deepface import DeepFace

class GUI:
    def __init__(self, root):
        # إعداد واجهة المستخدم الرسومية
        self.root = root
        self.root.title("برنامج كشف المشاعر")
        self.root.geometry("1370x710")  # تحديد حجم الواجهة
        self.root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

        # إضافة صورة خلفية
        self.background_image = Image.open("C:/Users/123/Desktop/GPT/AI.jpg")  # قم بتغيير اسم الصورة إلى اسم الصورة الخاصة بك
        self.background_image = self.background_image.resize((1370, 710), Image.BICUBIC)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)


        # الحصول على حجم الشاشة
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # حساب موقع النافذة المركزية
        x_position = (screen_width - 1370) // 2
        y_position = 0

        # تحديد موقع النافذة المركزية
        self.root.geometry(f"1370x710+{x_position}+{y_position}")

        # إنشاء نموذج DeepFace مع تحديد نوع النموذج "Emotion"
        self.deepface_model = DeepFace.build_model(model_name="Emotion")

        # # تحميل النموذج والتسميات
        # self.model = load_model("keras_model (2).h5", compile=False)
        # # قراءة محتوى ملف النص باستخدام ترميز UTF-8
        # self.class_names = open("labels (2).txt", "r", encoding="utf-8").readlines()
        # self.class_names = {0: 'Angry', 1: 'Fear', 2: 'Happy', 3: 'Neutral', 4: 'Sad', 5: 'Surprise'}

        # إنشاء مكان لعرض صورة الكاميرا
        self.camera_frame = tk.Label(root, width=700, height=500)
        self.camera_frame.pack(pady=0)

        # إنشاء مكان لعرض النص
        self.class_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), bg="#3498db", fg="white", wraplength=700)
        self.class_label.pack(pady=5)

        # إنشاء مكان لعرض زر التقاط صورة وتبديل الكاميرا  
        captur_toggle_buttons = tk.Label(root)
        captur_toggle_buttons.pack(pady=2)

        # إضافة زر إلتقاط صورة
        capture_button = tk.Button(captur_toggle_buttons, text="إلتقاط صورة", font=("Helvetica", 15), command=self.capture_image, width=25, height=1, bg="#3498db", fg="white")
        capture_button.pack(side="right", padx=25, pady=5)

        # إضافة زر تبديل كاميرا الويب
        toggle_webcam_button = tk.Button(captur_toggle_buttons, text="تبديل كاميرا الويب", font=("Helvetica", 15), command=self.toggle_webcam, width=25, height=1, bg="#3498db", fg="white")
        toggle_webcam_button.pack(side="left", padx=25, pady=5)


        # إنشاء مكان لعرض زر إيقاف الكاميرا وتحميل صورة  
        stop_load_buttons = tk.Label(root)
        stop_load_buttons.pack(pady=2)

        # إضافة زر إيقاف الكاميرا
        self.stop_camera_button = tk.Button(stop_load_buttons, text="إيقاف الكاميرا", font=("Helvetica", 15), command=self.toggle_camera, width=25, height=1, bg="#e74c3c", fg="white")
        self.stop_camera_button.pack(side="right", padx=25, pady=5)

        # إضافة زر لتحميل الصورة
        load_button = tk.Button(stop_load_buttons, text="تحميل صورة", font=("Helvetica", 15), command=self.load_image, width=25, height=1, bg="#2ecc71", fg="white")
        load_button.pack(side="left", padx=25, pady=5)

        # إضافة شريط في أسفل الواجهة (Footer)
        footer_label = tk.Label(root, text="تم التطوير بواسطة صفوان سعدان & حسام أحمد & عمار الشرعبي", font=("Helvetica", 15), bg="#2c3e50", fg="white")
        footer_label.pack(side="bottom", fill="x", pady=2)

        # إضافة متغير لتحديد ما إذا كان يجب عرض كاميرا الويب أم الصورة
        self.show_webcam = True

        # بدء تشغيل الكاميرا
        self.camera_running = True
        self.camera_thread = threading.Thread(target=self.update_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()

    def load_image(self):
         # فتح نافذة لاختيار الصورة
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        # إذا تم تحديد ملف
        if file_path:
            # قم بتخزين الصورة المؤقتة
            temp_image = Image.open(file_path)
            temp_image = temp_image.resize((700, 500), Image.BICUBIC)

            # عرض الصورة المؤقتة في المستطيل
            photo = ImageTk.PhotoImage(temp_image)
            self.camera_frame.config(image=photo)
            self.camera_frame.image = photo

            # حفظ الصورة المؤقتة للاستخدام في حالة تحليل الصورة
            self.captured_image = np.array(temp_image)

            # تحليل الصورة وطباعة الفئة
            self.analyze_image(self.captured_image)


    def analyze_image(self, image_array):
        # تحليل الصورة والطباعة
        image_array = cv2.resize(image_array, (224, 224), interpolation=cv2.INTER_AREA)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        image_array = (image_array / 255.0).astype(np.float32)
        image_array = image_array.reshape(1, 224, 224, 3)

        # تحليل الصورة باستخدام DeepFace
        result = DeepFace.analyze(image_array[0], enforce_detection=False)

        # الحصول على اسم المشاعر
        emotion = result['dominant_emotion']

        # طباعة التنبؤ ونسبة الثقة
        print("Emotion:", emotion)
        print("Confidence Score:", result[emotion])

        # تحديث التسمية في واجهة المستخدم
        self.class_label.config(text=emotion)

        # نص إلى كلام
        self.speak(emotion)

        
    def toggle_camera(self):
        # تغيير حالة تشغيل/إيقاف تشغيل الكاميرا
        self.camera_running = not self.camera_running

        if self.camera_running:
            self.stop_camera_button.config(text="إيقاف الكاميرا", bg="#e74c3c")
        else:
            self.stop_camera_button.config(text="تشغيل الكاميرا", bg="#2ecc71")
            
        
    def capture_image(self):
        # التقاط صورة من الكاميرا
        camera = cv2.VideoCapture(0)  # يمكن تعديل الرقم اعتمادًا على جهاز الكاميرا
        ret, image = camera.read()
        camera.release()

        # عرض الصورة الملتقطة في المستطيل
        image = cv2.resize(image, (700, 500), interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(Image.fromarray(image))
        self.camera_frame.config(image=photo)
        self.camera_frame.image = photo

        # حفظ الصورة الملتقطة للاستخدام في حالة تحليل الصورة
        self.captured_image = image

        # تحليل الصورة وطباعة الفئة
        self.analyze_image(self.captured_image)


    def toggle_webcam(self):
        # تبديل بين كاميرا الويب والصورة الملتقطة
        self.show_webcam = not self.show_webcam

    def update_camera(self):
        while True:
            if self.camera_running:
                if self.show_webcam:
                    webcam_source = 0
                else:
                    webcam_source = 1

                camera = cv2.VideoCapture(webcam_source)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

                ret, image = camera.read()

                # تعرف على الوجه باستخدام Haar Cascades
                if self.show_webcam:
                    faces = self.detect_faces(image)
                    self.draw_faces(image, faces)

                # تحديث إطار الكاميرا في واجهة المستخدم
                image = cv2.resize(image, (700, 500), interpolation=cv2.INTER_AREA)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

                # التحقق من نوع الكائن الذي تُرجعه image.resize
                if isinstance(image, Image.Image):
                    # تحويل الصورة إلى مصفوفة NumPy
                    image_array = np.asarray(image, dtype=np.uint8)  # قد تحتاج لتغيير النوع إلى uint8
                    image_array = (image_array / 255.0).astype(np.float32)
                    image_array = image_array.reshape(1, 700, 500, 3)

                    # تحليل الصورة باستخدام DeepFace
                    prediction = self.deepface_model.predict(image_array)

                    # القيم المتوقعة للمشاعر
                    # emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
                    emotion_labels = ['غاضب', 'مشمئز', 'خائف', 'سعيد', 'حزين', 'متفاجئ', 'محايد']

                    # احتمال المشاعر
                    emotion_probabilities = prediction.flatten()

                    # الفهم الكتابي للمشاعر واحتمالاتها
                    emotions_dict = dict(zip(emotion_labels, emotion_probabilities))

                    # الحصول على المشاعر المرتبة تنازليًا
                    sorted_emotions = sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True)

                    # الحصول على المشاعر الأكثر احتمالا ونسب الثقة
                    emotion, confidence_score = sorted_emotions[0]

                    # طباعة التنبؤ ونسبة الثقة
                    print("Emotion:", emotion)
                    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

                    # تحديث التسمية في واجهة المستخدم
                    self.class_label.config(text=emotion)

                elif hasattr(self, 'captured_image') and self.captured_image is not None:
                    # التنبؤ بالصورة الملتقطة
                    self.analyze_image(self.captured_image)

                # عرض الصورة على واجهة المستخدم
                photo = ImageTk.PhotoImage(image)
                self.camera_frame.config(image=photo)
                self.camera_frame.image = photo

                camera.release()

            self.root.update_idletasks()
            self.root.update()




    def detect_faces(self, frame):
        # استخدام Haar Cascades للكشف عن الوجوه
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
        return faces

    def draw_faces(self, frame, faces):
        # رسم مربعات حول الوجوه المكتشفة
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


    def speak(self, text):
        # تهيئة المترجم
        translator = Translator()
        # ترجمة النص إلى الإنجليزية
        english_text = translator.translate(text, dest='en').text

        # تهيئة محرك TTS
        engine = pyttsx3.init()
        # نطق النص المترجم
        engine.say(english_text)
        # انتظر انتهاء التحدث
        engine.runAndWait()


# إنشاء الجذر (root) وبدء التطبيق
root = tk.Tk()
app = GUI(root)
root.mainloop()