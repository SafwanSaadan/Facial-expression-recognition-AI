import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from keras.models import load_model
import numpy as np
import threading
from googletrans import Translator
import pyttsx3
# import webview  # استيراد وحدة الويب الجديدة
import eel  # استيراد وحدة الويب الجديدة

eel.init('web')  # إعداد مجلد الويب

class GUI:
    def __init__(self, root):
        # إعداد واجهة المستخدم الرسومية
        self.root = root
        self.root.title("برنامج كشف المشاعر")
        self.root.geometry("900x700")  # تحديد حجم الواجهة
        self.root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

        # الحصول على حجم الشاشة
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # حساب موقع النافذة المركزية
        x_position = (screen_width - 900) // 2
        y_position = 0

        # تحديد موقع النافذة المركزية
        self.root.geometry(f"900x700+{x_position}+{y_position}")

        # تحميل النموذج والتسميات
        self.model = load_model("keras_Model.h5", compile=False)
        # قراءة محتوى ملف النص باستخدام ترميز UTF-8
        self.class_names = open("labels.txt", "r", encoding="utf-8").readlines()

        # إنشاء مكان لعرض صورة الكاميرا
        self.camera_frame = tk.Label(root, bg="#3498db", width=900, height=500)
        self.camera_frame.pack(pady=0)

        # إنشاء مكان لعرض النص
        self.class_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), bg="#3498db", fg="white", wraplength=900)
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
            temp_image = temp_image.resize((900, 500), Image.BICUBIC)

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
        image_array = (image_array / 127.5) - 1
        image_array = image_array.reshape(1, 224, 224, 3)

        prediction = self.model.predict(image_array)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        confidence_score = prediction[0][index]

        # طباعة التنبؤ ونسبة الثقة
        class_name = class_name[2:].strip()  # إزالة الفراغات الرائدة
        print("Class:", class_name, end="")
        print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

        # تحديث التسمية في واجهة المستخدم
        self.class_label.config(text=class_name)

        # نص إلى كلام
        self.speak(class_name)

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
        image = cv2.resize(image, (900, 500), interpolation=cv2.INTER_AREA)
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
        if self.camera_running:
            if self.show_webcam:
                # عرض إطار كاميرا الويب
                webcam_source = 0
            else:
                # عرض الصورة الملتقطة بدلاً من إطار كاميرا الويب
                webcam_source = 1

            camera = cv2.VideoCapture(webcam_source)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            ret, image = camera.read()

            # تحديث إطار الكاميرا في واجهة المستخدم
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = image.resize((900, 500), Image.BICUBIC)
            photo = ImageTk.PhotoImage(image)

            # التأكد من أن العمليات تحدث في الخيط الرئيسي باستخدام after
            self.camera_frame.after(10, lambda: self.camera_frame.config(image=photo))
            
            # التنبؤ بنموذج الشبكة إذا كان يتم عرض كاميرا الويب
            if self.show_webcam:
                image_array = image.resize((224, 224), Image.BICUBIC)
                image_array = np.asarray(image_array, dtype=np.float32)
                image_array = (image_array / 127.5) - 1
                image_array = image_array.reshape(1, 224, 224, 3)

                prediction = self.model.predict(image_array)
                index = np.argmax(prediction)
                class_name = self.class_names[index]
                confidence_score = prediction[0][index]

                # طباعة التنبؤ ونسبة الثقة
                class_name = class_name[2:].strip()  # إزالة الفراغات الرائدة
                print("Class:", class_name, end="")
                print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

                # تحديث التسمية في واجهة المستخدم
                self.class_label.config(text=class_name)

            elif hasattr(self, 'captured_image') and self.captured_image is not None:
                # التنبؤ بالصورة الملتقطة
                self.analyze_image(self.captured_image)

            camera.release()

        # استمرار تحديث واجهة المستخدم بانتظام
        self.root.after(10, self.update_camera)

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
# root.mainloop()

# تحويل واجهة Tkinter إلى نافذة ويب
# webview.create_window("Emotion Detection App", app.root, width=900, height=700, resizable=False)
# webview.start()

@eel.expose
def load_image():
    app.load_image()

@eel.expose
def toggle_camera():
    app.toggle_camera()

@eel.expose
def capture_image():
    app.capture_image()

@eel.expose
def toggle_webcam():
    app.toggle_webcam()

# بدء التشغيل النصي
eel.start('web/indxe.html', size=(900, 700))
