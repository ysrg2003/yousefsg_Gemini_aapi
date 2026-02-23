import asyncio
import sys
import json
import os
import shutil
import zipfile
import stat  # ميزة: التحكم في نظام ملفات لينكس

# ==========================================================
# 1. نظام إدارة البيئة الدائمة (Persistence Layer)
# ==========================================================
current_dir = os.getcwd()
zip_path = os.path.join(current_dir, "vendor_assets.zip")
extract_path = os.path.join(current_dir, "vendor_extracted")

# ميزة: فك الضغط التلقائي والذكي (لا يكرر الفك إذا كان المجلد موجوداً)
if os.path.exists(zip_path) and not os.path.exists(extract_path):
    print("📦 جاري فك ضغط المحرك الدائم (Libraries & Browsers)...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # ميزة: إصلاح الصلاحيات (التي منعت التشغيل سابقاً)
    # نقوم بمنح صلاحية التنفيذ لـ Node.js ومحركات المتصفح
    print("🔑 جاري إصلاح صلاحيات الملفات التنفيذية...")
    for root, dirs, files in os.walk(extract_path):
        for name in files:
            if name == "node" or "chrome" in name or "firefox" in name or name.endswith(".sh"):
                file_path = os.path.join(root, name)
                st = os.stat(file_path)
                os.chmod(file_path, st.st_mode | stat.S_IEXEC)
    print("✅ تم تجهيز البيئة ومنح الصلاحيات بنجاح.")

# ==========================================================
# 2. حقن المسارات (Path Injection)
# ==========================================================
vendor_python = os.path.join(extract_path, "python")
sys.path.insert(0, vendor_python) # الأولوية للمكتبات المرفوعة
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")

# ==========================================================
# 3. الاستيراد الآمن (Safe Import)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم تحميل محرك Camoufox بنجاح.")
except ImportError as e:
    print(f"❌ خطأ فادح: لم يتم العثور على مكتبة Camoufox في المسار: {vendor_python}")
    print(f"التفاصيل: {e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 4. المحرك الأساسي للأتمتة (Automation Engine)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🚀 بدء العملية... السؤال: {prompt}")
    
    # ميزة: التخفي الكامل (Full Stealth) عبر Camoufox
    async with AsyncCamoufox(
        headless=True,
        # هنا يمكن إضافة خيارات متقدمة مثل إحداثيات وهمية إذا رغبت مستقبلاً
    ) as browser:
        
        # ميزة: سياق متصفح مع بصمة حقيقية (Fingerprinting)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # ميزة: تجاوز تسجيل الدخول (Session Persistence)
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم تحميل الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # ميزة: صواريخ السرعة (Turbo Speed) - منع تحميل 90% من البيانات غير الضرورية
        # نحذف الصور، الخطوط، والستايلات لتوفير الوقت والبيانات
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري فتح Gemini باستخدام البيئة الدائمة...")
            # ميزة: الانتظار السريع (Fast Navigation)
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # ميزة: المحدد الذكي (Smart Selector) لمربع النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=20000)
            
            print("✍️ كتابة السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 تم الإرسال، بانتظار الرد...")

            # ميزة: الانتظار المبني على الأحداث (Event-based Waiting)
            # ننتظر ظهور زر المشاركة أو التفاعل الذي يظهر فقط بعد اكتمال النص
            finish_selector = "button[aria-label*='Good response'], button[aria-label*='Share']"
            await page.wait_for_selector(finish_selector, timeout=60000)

            # ميزة: استخراج المحتوى بدقة (Content Scraping)
            # جلب آخر إجابة ظهرت في المحادثة
            result_text = await page.evaluate('''() => {
                const responses = document.querySelectorAll(".model-response-text");
                if (responses.length > 0) {
                    return responses[responses.length - 1].innerText;
                }
                return "لم يتم العثور على نص الرد.";
            }''')

            output = {
                "status": "success",
                "prompt": prompt,
                "response": result_text
            }
            print("✅ تم استلام الرد بنجاح.")

        except Exception as e:
            print(f"❌ حدث خطأ أثناء التشغيل: {str(e)}")
            # ميزة: لقطة شاشة للخطأ (Error Debugging)
            await page.screenshot(path="error_debug.png")
            output = {
                "status": "error",
                "message": str(e)
            }

        # ميزة: تصدير البيانات المهيكلة (Structured JSON)
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

# ==========================================================
# 5. نقطة الانطلاق (Entry Point)
# ==========================================================
if __name__ == "__main__":
    # ميزة: دعم البرومبت من سطر الأوامر (CLI Support)
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello Gemini"
    asyncio.run(run_gemini_automation(user_prompt))
