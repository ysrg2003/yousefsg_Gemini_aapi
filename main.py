import asyncio
import sys
import json
import os
import shutil
import zipfile
import stat  # للتحكم في صلاحيات نظام Linux

# ==========================================================
# 1. إدارة البيئة الدائمة (إصلاح صلاحيات التنفيذ)
# ==========================================================
current_dir = os.getcwd()
zip_path = os.path.join(current_dir, "vendor_assets.zip")
extract_path = os.path.join(current_dir, "vendor_extracted")

if os.path.exists(zip_path) and not os.path.exists(extract_path):
    print("📦 جاري فك ضغط المحرك الدائم...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    print("🔑 إصلاح صلاحيات الملفات (تجنب Permission Denied)...")
    for root, dirs, files in os.walk(extract_path):
        for name in files:
            if name == "node" or "chrome" in name or "firefox" in name or name.endswith(".sh"):
                file_path = os.path.join(root, name)
                st = os.stat(file_path)
                os.chmod(file_path, st.st_mode | stat.S_IEXEC)
    print("✅ البيئة جاهزة تماماً.")

# ==========================================================
# 2. إعداد المسارات المخصصة (Path Redirection)
# ==========================================================
vendor_python = os.path.join(extract_path, "python")
sys.path.insert(0, vendor_python) 
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")

# ==========================================================
# 3. استيراد المحرك (Stealth Engine)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم تحميل محرك Camoufox بنجاح.")
except ImportError as e:
    print(f"❌ خطأ في المكتبات المرفوعة: {e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 4. وظيفة الأتمتة الرئيسية (Core Automation)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🚀 تشغيل العملية... السؤال: {prompt}")
    
    async with AsyncCamoufox(headless=True) as browser:
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # تحميل الجلسة (Cookies) لضمان تسجيل الدخول
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم استعادة الجلسة بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # ميزة السرعة القصوى (النسخة الذكية):
        # نمنع الصور والخطوط فقط. تركنا الـ CSS لضمان عمل الواجهة بشكل سليم.
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري الدخول إلى Gemini...")
            # ننتظر استقرار الشبكة لضمان ظهور مربع النص
            await page.goto(GEMINI_URL, wait_until="networkidle", timeout=60000)

            # ميزة التحديد الذكي لمربع النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=20000)
            
            print("✍️ إرسال السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 بانتظار توليد الرد (الانتظار الذكي)...")

            # ميزة استخراج النص (بدلاً من انتظار الأزرار المتقلبة)
            response_selector = ".model-response-text"
            try:
                # ننتظر ظهور أول إشارة للرد
                await page.wait_for_selector(response_selector, timeout=60000)
                # مهلة 5 ثوانٍ لضمان اكتمال الكتابة (Streaming)
                await asyncio.sleep(5)
            except:
                print("⚠️ تنبيه: استغرق الرد وقتاً طويلاً، سأحاول جلب ما ظهر.")

            # ميزة الكشط البرمجي العميق (Deep Scrape)
            result_text = await page.evaluate('''() => {
                const responses = document.querySelectorAll(".model-response-text");
                if (responses.length > 0) {
                    return responses[responses.length - 1].innerText;
                }
                const fallback = document.querySelector(".message-content");
                return fallback ? fallback.innerText : "فشل استخراج النص.";
            }''')

            output = {
                "status": "success",
                "prompt": prompt,
                "response": result_text
            }
            print("✅ اكتملت المهمة بنجاح.")

        except Exception as e:
            print(f"❌ خطأ تشغيلي: {str(e)}")
            # ميزة تصحيح الأخطاء البصرية
            await page.screenshot(path="error_debug.png")
            output = {"status": "error", "message": str(e)}

        # حفظ النتيجة النهائية
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

# ==========================================================
# 5. نقطة الدخول (Execution)
# ==========================================================
if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "Hi Gemini"
    asyncio.run(run_gemini_automation(p))
