import os
import subprocess
import shutil
import sys

def setup():
    # تنظيف المجلدات القديمة لضمان بناء "نظيف"
    vendor_dir = "vendor"
    if os.path.exists(vendor_dir):
        print(f"🗑️ تنظيف المجلد القديم...")
        shutil.rmtree(vendor_dir)
    
    python_dir = os.path.join(vendor_dir, "python")
    browsers_dir = os.path.join(vendor_dir, "browsers")
    
    os.makedirs(python_dir, exist_ok=True)
    os.makedirs(browsers_dir, exist_ok=True)
    
    print("⏳ بدأت عملية بناء الترسانة (Assets Building)...")
    
    # 1. تثبيت المكتبات الأساسية
    # استخدمنا --no-cache-dir لضمان عدم سحب نسخ قديمة ومعطوبة
    libs = ["playwright", "camoufox", "wheel", "setuptools"]
    
    print(f"📦 تثبيت المكتبات البرمجية: {', '.join(libs)}")
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        *libs, 
        "--target", python_dir,
        "--no-cache-dir"
    ], check=True)

    # 2. إعداد مسار المتصفحات وتحميلها
    # نضع المتصفحات داخل مجلد vendor لتدخل في ملف الـ ZIP
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath(browsers_dir)
    
    print("🌐 تحميل محركات المتصفح (Chromium & Camoufox Fetch)...")
    # تحميل Chromium فقط لتقليل الحجم (فهو يكفي لـ Gemini)
    subprocess.run([
        sys.executable, "-m", "playwright", "install", "chromium"
    ], check=True)
    
    # تحميل بيانات التخفي الخاصة بـ Camoufox
    subprocess.run([
        sys.executable, "-m", "camoufox", "fetch"
    ], check=True)

    # 3. تنظيف المجلدات المؤقتة لتقليل حجم الـ ZIP
    print("🧹 تنظيف ملفات الكاش غير الضرورية...")
    for root, dirs, files in os.walk(python_dir):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))

    # 4. الضغط النهائي
    print("🗜️ جاري ضغط الترسانة إلى vendor_assets.zip...")
    # نقوم بالضغط بحيث يكون محتوى مجلد vendor هو جذور الملف المضغوط
    shutil.make_archive("vendor_assets", 'zip', vendor_dir)
    
    # تنظيف المجلد بعد الضغط لتوفير مساحة في الـ Runner
    shutil.rmtree(vendor_dir)
    
    print("✅ اكتملت المهمة! الملف جاهز للرفع إلى GitHub Releases.")

if __name__ == "__main__":
    setup()
