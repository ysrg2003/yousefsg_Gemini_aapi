import asyncio
import sys
import json
import os
import shutil
import zipfile
import stat  # ميزة: التحكم في صلاحيات نظام Linux لمنع Permission Denied

# ==========================================================
# 1. نظام إدارة البيئة الدائمة (Persistence & Permissions)
# ==========================================================
current_dir = os.getcwd()
zip_path = os.path.join(current_dir, "vendor_assets.zip")
extract_path = os.path.join(current_dir, "vendor_extracted")

# ميزة: فك الضغط التلقائي والذكي (لا يكرر الفك إذا وجد المجلد)
if os.path.exists(zip_path) and not os.path.exists(extract_path):
    print("📦 جاري فك ضغط المحرك الدائم (Libraries & Browsers)...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # ميزة: إصلاح الصلاحيات (الحل الجذري والنهائي لخطأ Permission Denied)
    print("🔑 جاري إصلاح صلاحيات الملفات التنفيذية...")
    for root, dirs, files in os.walk(extract_path):
        for name in files:
            # منح صلاحية التنفيذ لملف node ومحركات المتصفح والسكربتات
            if name == "node" or "chrome" in name or "firefox" in name or name.endswith(".sh"):
                file_path = os.path.join(root, name)
                st = os.stat(file_path)
                os.chmod(file_path, st.st_mode | stat.S_IEXEC)
    print("✅ تم تجهيز البيئة ومنح الصلاحيات بنجاح.")

# ==========================================================
# 2. حقن المسارات المخصصة (Path Redirection)
# ==========================================================
# ميزة: استخدام المكتبات المرفوعة دون الحاجة لتحميلها في كل مرة (Persistence)
vendor_python = os.path.join(extract_path, "python")
sys.path.insert(0, vendor_python) 
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")

# ==========================================================
# 3. الاستيراد الآمن لمحرك التخفي (Stealth Engine)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم تحميل محرك Camoufox بنجاح.")
except ImportError as e:
    print(f"❌ خطأ فادح: المكتبات غير موجودة في المسار المحدد. {e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 4. المحرك الأساسي للأتمتة والذكاء (Core Engine)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🚀 بدء المهمة العملاقة... السؤال: {prompt}")
    
    # ميزة: التخفي الكامل (Stealth Mode) عبر Camoufox
    async with AsyncCamoufox(headless=True) as browser:
        
        # ميزة: بصمة جهاز حقيقية (Fingerprinting) لمحاكاة البشر
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # ميزة: تجاوز تسجيل الدخول (Session Persistence) عبر الكوكيز
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم استعادة الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # ميزة صواريخ السرعة (Turbo Speed): حظر الصور والخطوط فقط
        # أبقينا على الـ CSS لضمان عدم "عمى" المتصفح عن النصوص الجديدة
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري الدخول إلى Gemini...")
            # ميزة: الانتظار السريع لهيكل الصفحة (DOM) لضمان السرعة
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # ميزة: المحدد الذكي (Smart Selector) لمربع النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ كتابة السؤال وإرساله...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            # --- ميزة: مراقب التدفق والتمرير الذكي (Streaming & Auto-Scroll) ---
            print("📡 بانتظار الرد (مراقبة النمو + التمرير التلقائي)...")
            response_selector = ".model-response-text"
            
            # ننتظر ظهور أول إشارة للرد
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_checks = 0
            
            # حلقة مراقبة الردود الطويلة (تصل لـ 80 ثانية للردود الضخمة)
            for i in range(40): 
                current_text = await page.evaluate(f'''() => {{
                    const res = document.querySelectorAll("{response_selector}");
                    return res.length > 0 ? res[res.length - 1].innerText : "";
                }}''')
                
                current_length = len(current_text)
                
                if current_length > previous_length:
                    print(f"✍️ Gemini يكتب... ({current_length} حرف)")
                    
                    # --- ميزة الـ Scroll التلقائي ---
                    # نمرر للأسفل في كل مرة ينمو فيها النص لضمان رؤية الصفحة كاملة
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    
                    previous_length = current_length
                    stable_checks = 0 # تصفير العداد لأن النص لا يزال ينمو
                else:
                    stable_checks += 1
                
                # إذا استقر النص لـ 3 فحوصات متتالية (6 ثوانٍ)، نعتبره انتهى
                if stable_checks >= 3 and current_length > 0:
                    print("✅ توقف النص عن النمو، تم اكتمال الإجابة.")
                    break
                
                await asyncio.sleep(2)

            # ميزة: استخراج النص النهائي بدقة (Deep Scrape)
            final_text = await page.evaluate('''() => {
                const responses = document.querySelectorAll(".model-response-text");
                return responses.length > 0 ? responses[responses.length - 1].innerText : "فشل استخراج النص.";
            }''')

            output = {
                "status": "success",
                "prompt": prompt,
                "response": final_text
            }
            print("✅ المهمة اكتملت بنجاح.")

        except Exception as e:
            print(f"❌ خطأ تشغيلي: {str(e)}")
            # ميزة: لقطة شاشة للخطأ للمساعدة في التصحيح البصري
            await page.screenshot(path="error_debug.png")
            output = {"status": "error", "message": str(e)}

        # ميزة: حفظ النتيجة بتنسيق JSON مهيكل وجاهز للاستخدام
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "Hi Gemini"
    asyncio.run(run_gemini_automation(p))

