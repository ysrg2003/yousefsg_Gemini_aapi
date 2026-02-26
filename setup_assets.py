import os
import subprocess
import shutil
import sys

def setup():
    # 1. إعداد المسارات الأساسية
    vendor_dir = "vendor"
    current_path = os.getcwd()
    
    python_dir = os.path.join(current_path, vendor_dir, "python")
    browsers_dir = os.path.join(current_path, vendor_dir, "browsers")
    # هذا المجلد سيحتوي على محتويات ~/.cache/camoufox بالكامل
    camou_cache_dir = os.path.join(current_path, vendor_dir, "camoufox_cache")

    # تنظيف أي مخلفات سابقة لضمان بناء نظيف
    if os.path.exists(vendor_dir):
        print("🧹 تنظيف مخلفات البناء السابق...")
        shutil.rmtree(vendor_dir)
    
    os.makedirs(python_dir, exist_ok=True)
    os.makedirs(browsers_dir, exist_ok=True)
    # ملاحظة: لا ننشئ camou_cache_dir هنا يدوياً، shutil.copytree ستنشئه لاحقاً

    print("⏳ بدأت عملية بناء الترسانة الشاملة (النسخة المحدثة)...")

    # 2. إعداد بيئة التنفيذ
    env = os.environ.copy()
    env["PYTHONPATH"] = python_dir + os.pathsep + env.get("PYTHONPATH", "")
    env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_dir

    # 3. تثبيت المكتبات البرمجية
    print("📦 تثبيت المكتبات (Playwright & Camoufox)...")
    libs = ["playwright", "camoufox", "wheel", "setuptools"]
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        *libs, 
        "--target", python_dir,
        "--no-cache-dir"
    ], check=True)

    # 4. تحميل متصفح Chromium الخاص بـ Playwright
    print("🌐 تحميل محرك Chromium...")
    subprocess.run([
        sys.executable, "-m", "playwright", "install", "chromium"
    ], env=env, check=True)
    
    # 5. تحميل محرك Camoufox الثقيل
    print("🦊 سحب محرك Camoufox إلى المسار الافتراضي...")
    # نتركه يحمله في المسار الافتراضي ~/.cache/camoufox أولاً لضمان سلامة الملفات
    subprocess.run([
        sys.executable, "-m", "camoufox", "fetch"
    ], env=env, check=True)
    
    # نقل الكاش من المسار الافتراضي إلى مجلد الـ vendor الخاص بنا
    default_cache = os.path.expanduser("~/.cache/camoufox")
    if os.path.exists(default_cache):
        print(f"🚚 نقل الكاش من {default_cache} إلى {camou_cache_dir}...")
        shutil.copytree(default_cache, camou_cache_dir)
    else:
        print("❌ خطأ: لم يتم العثور على الكاش المحمل!")
        sys.exit(1)

    # 6. تنظيف الملفات الزائدة لتقليل الحجم
    print("🧹 تنظيف عميق لتقليل الحجم إلى أقصى حد...")
    # قائمة بالمجلدات التي لا نحتاجها إطلاقاً لتشغيل Gemini
    shutil_targets = [
        "python/share", "python/include", # ملفات تطوير لا لزوم لها
        "browsers/chromium_headless_shell-1208/locales", # لغات المتصفح (نحتاج الإنجليزية فقط)
        "browsers/chromium_headless_shell-1208/swiftshader", # معالجة رسومية لا نحتاجها في Headless
        "camoufox_cache/dictionaries", # القواميس
    ]
    
    for target in shutil_targets:
        full_path = os.path.join(vendor_dir, target)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"🗑️ تم حذف: {target}")

    # حذف ملفات محددة بالامتداد
    for root, dirs, files in os.walk(vendor_dir):
        for file in files:
            if file.endswith(('.pdb', '.pyc', '.exe', '.txt', '.md')): # ملفات تصحيح وتوثيق
                os.remove(os.path.join(root, file))
                
    
    # 7. عملية الضغط النهائي
    # استبدل سطر الضغط القديم بهذا الجزء:
    print(f"🗜️ جاري الضغط بتقنية Zstd الفائقة...")
    # c: create, I: use zstd, f: file
    # سنقوم بضغط محتويات مجلد vendor
    try:
        subprocess.run([
            "tar", "--zstd", "-cf", "vendor_assets.tar.zst", "-C", vendor_dir, "."
        ], check=True)
        
        size_mb = os.path.getsize("vendor_assets.tar.zst") / (1024 * 1024)
        print(f"✅ تم إنشاء الترسانة (Zstd) بنجاح! الحجم: {size_mb:.2f} MB")
        shutil.rmtree(vendor_dir)
    except Exception as e:
        print(f"❌ فشل ضغط Zstd: {e}")
        sys.exit(1)

    

if __name__ == "__main__":
    setup()
