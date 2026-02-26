import os
import subprocess
import shutil
import sys

def setup():
    vendor_dir = "vendor"
    if os.path.exists(vendor_dir):
        shutil.rmtree(vendor_dir)
    
    # تعريف المسارات بشكل مطلق لضمان عدم ضياع subprocess
    current_path = os.getcwd()
    python_dir = os.path.join(current_path, vendor_dir, "python")
    browsers_dir = os.path.join(current_path, vendor_dir, "browsers")
    camou_cache_dir = os.path.join(current_path, vendor_dir, "camoufox_cache")
    
    os.makedirs(python_dir, exist_ok=True)
    os.makedirs(browsers_dir, exist_ok=True)
    os.makedirs(camou_cache_dir, exist_ok=True)
    
    print("⏳ بدأت عملية بناء الترسانة الشاملة (حجم الملف المتوقع ~800MB)...")

    # 1. تثبيت المكتبات
    libs = ["playwright", "camoufox", "wheel", "setuptools"]
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        *libs, 
        "--target", python_dir,
        "--no-cache-dir"
    ], check=True)

    # إعداد البيئة المؤقتة لعملية التحميل فقط
    env = os.environ.copy()
    env["PYTHONPATH"] = python_dir + os.pathsep + env.get("PYTHONPATH", "")
    env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_dir
    env["CAMOUFOX_CACHE_DIR"] = camou_cache_dir # هنا يتم الحجز!

    print("🌐 تحميل Chromium...")
    subprocess.run([
        sys.executable, "-m", "playwright", "install", "chromium"
    ], env=env, check=True)
    
    print("🦊 سحب محرك Camoufox (البيانات والارتباطات)...")
    # هذا الأمر هو الذي سيملأ مجلد camoufox_cache
    subprocess.run([
        sys.executable, "-m", "camoufox", "fetch"
    ], env=env, check=True)

    # تنظيف الكاشات التي لا لزوم لها لتقليل حجم الـ ZIP
    print("🧹 تنظيف الملفات الزائدة...")
    for root, dirs, files in os.walk(vendor_dir):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))

    print(f"🗜️ جاري ضغط الترسانة... قد يستغرق هذا وقتاً على GitHub Actions...")
    # ملاحظة: الضغط يتم لمحتوى مجلد vendor وليس المجلد نفسه
    shutil.make_archive("vendor_assets", 'zip', vendor_dir)
    
    # لا تحذف المجلد قبل التأكد من انتهاء الضغط
    if os.path.exists("vendor_assets.zip"):
        shutil.rmtree(vendor_dir)
        print("✅ تم إنشاء vendor_assets.zip بنجاح شاملة كل شيء!")
    else:
        print("❌ فشل إنشاء ملف الـ ZIP!")

if __name__ == "__main__":
    setup()
