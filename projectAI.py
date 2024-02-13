# استيراد المكتبات الضرورية
import tkinter as tk  # استيراد مكتبة Tkinter وتعيين اسمها كـ tk
from tkinter import filedialog  # استيراد واجهة filedialog من مكتبة Tkinter
from PIL import Image, ImageTk  # استيراد مكتبتي PIL للتعامل مع الصور و ImageTk لعرض الصور في Tkinter
import cv2  # استيراد مكتبة OpenCV لمعالجة الصور والفيديو
from keras.models import load_model  # استيراد وظيفة load_model من مكتبة Keras لتحميل نموذج الشبكة العصبية
import numpy as np  # استيراد مكتبة NumPy لمعالجة البيانات
import threading  # استيراد مكتبة threading للتعامل مع عمليات متعددة الخيوط
from googletrans import Translator  # استيراد مكتبة googletrans لترجمة النصوص
import pyttsx3  # استيراد مكتبة pyttsx3 لتحويل النص إلى كلام
from deepface import DeepFace  # استيراد مكتبة DeepFace للتعرف على الوجوه وتحليلها

# تعريف كلاس الواجهة
class GUI:
    # كنستركتور __init__  تعريف دالة البداية
    def __init__(self, root): # self تعمل مثل this
        # إعداد واجهة المستخدم الرسومية
        self.root = root
        self.root.title("برنامج كشف المشاعر")
        self.root.geometry("1370x710")  # تحديد حجم الواجهة
        self.root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

        # إضافة صورة خلفية
        self.background_image = Image.open("C:/Users/123/Desktop/GPT/AI.jpg")  # فتح صورة الخلفية
        self.background_image = self.background_image.resize((1370, 710), Image.BICUBIC)  # تغيير حجم الصورة
        self.background_photo = ImageTk.PhotoImage(self.background_image)  # تحويل الصورة إلى PhotoImage لعرضها في Tkinter
        self.background_label = tk.Label(root, image=self.background_photo)  # إنشاء علامة (Label) لعرض الصورة
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)  # تحديد مكان وحجم الصورة في النافذة


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
        self.camera_running = True  # تعيين حالة تشغيل الكاميرا إلى True
        self.camera_thread = threading.Thread(target=self.update_camera)  # إنشاء خيط لتحديث الكاميرا
        self.camera_thread.daemon = True  # تعيين الخيط كخيط ديمون ليتوقف تلقائيًا عند إغلاق البرنامج
        self.camera_thread.start()  # بدء تنفيذ الخيط



    # تعريف الدالة لتحميل الصورة
    def load_image(self):
         # فتح نافذة لاختيار الصورة
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        # إذا تم تحديد ملف
        if file_path:
            # قم بتخزين الصورة المؤقتة
            temp_image = Image.open(file_path)  # فتح الصورة باستخدام مكتبة PIL
            temp_image = temp_image.resize((700, 500), Image.BICUBIC)  # تغيير حجم الصورة لتناسب واجهة المستخدم

            # عرض الصورة المؤقتة في واجهة المستخدم
            photo = ImageTk.PhotoImage(temp_image)  # تحويل الصورة إلى PhotoImage لعرضها في Tkinter
            self.camera_frame.config(image=photo)  # تحديث إطار الكاميرا بالصورة المؤقتة
            self.camera_frame.image = photo  # حفظ الصورة لتجنب تسريب الذاكرة

            # حفظ الصورة المؤقتة للاستخدام في حالة تحليل الصورة
            self.captured_image = np.array(temp_image)

            # تحليل الصورة وطباعة الفئة
            self.analyze_image(self.captured_image)




    # تعريف الدالة لتحليل الصورة
    def analyze_image(self, image_array):
        # تغيير حجم الصورة وتحويل تنسيق الألوان إلى RGB
        image_array = cv2.resize(image_array, (224, 224), interpolation=cv2.INTER_AREA)  # تغيير حجم الصورة إلى 224x224 بكسل
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)  # تحويل تنسيق الألوان إلى RGB
        image_array = (image_array / 255.0).astype(np.float32)  # تحويل نطاق القيم إلى [0، 1]
        image_array = image_array.reshape(1, 224, 224, 3)  # إعداد الصورة للتحليل

        # تحليل الصورة باستخدام DeepFace
        result = DeepFace.analyze(image_array[0], enforce_detection=False)

        # الحصول على اسم المشاعر
        emotion = result[0]['dominant_emotion']

        # طباعة التنبؤ ونسبة الثقة
        print("Emotion:", emotion)
        print("Confidence Score:", result[emotion])

        # تحديث التسمية في واجهة المستخدم
        self.class_label.config(text=emotion)

        # نص إلى كلام
        self.speak(emotion)



        
    # تعريف الدالة لتبديل حالة تشغيل/إيقاف تشغيل الكاميرا
    def toggle_camera(self):
        # تغيير حالة تشغيل/إيقاف تشغيل الكاميرا
        self.camera_running = not self.camera_running

        # التحقق من حالة تشغيل الكاميرا لتحديد نص زر إيقاف التشغيل/التشغيل
        if self.camera_running:
            self.stop_camera_button.config(text="إيقاف الكاميرا", bg="#e74c3c")  # تغيير نص الزر ولونه إلى أحمر
        else:
            self.stop_camera_button.config(text="تشغيل الكاميرا", bg="#2ecc71")  # تغيير نص الزر ولونه إلى أخضر
            



    # تعريف الدالة لالتقاط صورة من الكاميرا
    def capture_image(self):
        # التقاط صورة من الكاميرا باستخدام OpenCV
        camera = cv2.VideoCapture(0)  # يمكن تعديل الرقم اعتمادًا على جهاز الكاميرا
        ret, image = camera.read()
        camera.release()  # إطلاق الكاميرا بعد التقاط الصورة

        # تغيير حجم الصورة وتحويل تنسيق الألوان إلى RGB
        image = cv2.resize(image, (700, 500), interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # عرض الصورة الملتقطة في واجهة المستخدم
        photo = ImageTk.PhotoImage(Image.fromarray(image))
        self.camera_frame.config(image=photo)
        self.camera_frame.image = photo  # حفظ الصورة لتجنب تسريب الذاكرة


        # حفظ الصورة الملتقطة للاستخدام في حالة تحليل الصورة
        self.captured_image = image

        # تحليل الصورة وطباعة الفئة
        self.analyze_image(self.captured_image)



    # تعريف الدالة لتبديل بين الكاميرا والصورة الملتقطة
    def toggle_webcam(self):
        # تبديل بين كاميرا الويب والصورة الملتقطة
        self.show_webcam = not self.show_webcam



    # تعريف الدالة التي تقوم بتحديث إطار الكاميرا
    def update_camera(self):
        # دورة تكرارية للتحديث مستمرة
        while True:
            # التحقق مما إذا كانت الكاميرا تعمل
            if self.camera_running:
                # تحديد مصدر الكاميرا حسب إعدادات العرض
                if self.show_webcam:
                    webcam_source = 0  # إعدادات العرض لكاميرا الويب
                else:
                    webcam_source = 2  # إعدادات العرض لكاميرا خارجية

                # تهيئة الكاميرا باستخدام OpenCV
                camera = cv2.VideoCapture(webcam_source)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # تعيين عرض الإطار
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # تعيين ارتفاع الإطار

                # قراءة إطار الكاميرا
                ret, image = camera.read()

                # كشف الوجوه باستخدام Haar Cascades إذا كانت عملية عرض الكاميرا مُفعلة
                if self.show_webcam:
                    faces = self.detect_faces(image)  # استدعاء دالة كشف الوجوه
                    self.draw_faces(image, faces)  # رسم الوجوه المكتشفة على الإطار

                # تغيير حجم الإطار لعرضه في واجهة المستخدم
                image = cv2.resize(image, (700, 500), interpolation=cv2.INTER_AREA)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # تحويل تنسيق الألوان إلى RGB
                image = Image.fromarray(image)  # تحويل الصورة إلى كائن Image

                # التحقق من نوع الكائن المُرجع من image.resize
                if isinstance(image, Image.Image):
                    # تحويل الصورة إلى مصفوفة NumPy
                    image_array = np.asarray(image, dtype=np.uint8)
                    image_array = (image_array / 255.0).astype(np.float32)  # تحويل نطاق القيم إلى [0، 1]
                    image_array = image_array.reshape(1, 700, 500, 3)  # إعداد الصورة للتحليل

                    # التحليل باستخدام DeepFace
                    prediction = self.deepface_model.predict(image_array)

                    # ترميز المشاعر واحتمالاتها
                    emotion_labels = ['غاضب', 'مشمئز', 'خائف', 'سعيد', 'حزين', 'متفاجئ', 'محايد']
                    emotion_probabilities = prediction.flatten()

                    # ترتيب المشاعر بحسب الاحتماليات
                    emotions_dict = dict(zip(emotion_labels, emotion_probabilities))
                    sorted_emotions = sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True)

                    # الحصول على المشاعر الأكثر احتمالا ونسب الثقة
                    emotion, confidence_score = sorted_emotions[0]
                    confidence_score = str(np.round(confidence_score * 100))[:-2]

                    # طباعة المشاعر ونسبة الثقة
                    print("المشاعر:", emotion)
                    print("نسبة الثقة:", confidence_score, "%")

                    emotion_score = "%" + emotion + " بنسبة :  " + confidence_score
                    # تحديث تسمية الفئة في واجهة المستخدم
                    self.class_label.config(text=emotion_score)

                    # نص إلى كلام
                    self.speak(emotion_score)

                # إذا كانت الكاميرا غير مُفعلة وكان هناك صورة تم التقاطها
                elif hasattr(self, 'captured_image') and self.captured_image is not None:
                    self.analyze_image(self.captured_image)  # تحليل الصورة الملتقطة

                # عرض الصورة على واجهة المستخدم
                photo = ImageTk.PhotoImage(image)
                self.camera_frame.config(image=photo)
                self.camera_frame.image = photo  # حفظ الصورة لتجنب حدوث تسريب الذاكرة

                camera.release()  # إطلاق الكاميرا بمجرد الانتهاء من استخدامها

            self.root.update_idletasks()  # تحديث عناصر واجهة المستخدم
            self.root.update()  # تحديث النافذة



    # تعريف الدالة التي تكشف الوجوه في الإطار
    def detect_faces(self, frame):
        # استخدام Haar Cascades لكشف الوجوه
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # تحويل الإطار إلى درجات الرمادي
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)  # الكشف عن الوجوه
        return faces  # إرجاع قائمة الوجوه المكتشفة



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
root = tk.Tk()  # إنشاء نافذة رسومية جديدة
app = GUI(root) # إنشاء كائن من الكلاس GUI وتمرير النافذة كمعامل
root.mainloop() # تشغيل نافذة البرنامج
