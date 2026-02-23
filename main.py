import asyncio
import sys
import json
import os

# --- إعداد المسارات الدائمة (يجب أن تكون في قمة الملف) ---
current_dir = os.getcwd()
vendor_python = os.path.join(current_dir, "vendor/python")
# إجبار بايثون على النظر داخل مجلد المكتبات المرفوع
sys.path.insert(0, vendor_python) 

# تحديد مسار المتصفح المرفوع لـ Playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(current_dir, "vendor/browsers")
# ------------------------------------------------------

# الاستيراد الآن من المجلد المرفوع
try:
    from camoufox.async_api import AsyncCamoufox
except ImportError:
    print("❌ خطأ: لم يتم العثور على مكتبة Camoufox في مجلد vendor.")
    print("تأكد من تشغيل 'Build Permanent Environment' أولاً.")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

async def run_gemini_automation(prompt):
    print(f"🚀 بدء العملية... السؤال: {prompt}")
    
    # تشغيل متصفح Camoufox بإعدادات التخفي الكاملة (بدون اختصار)
    async with AsyncCamoufox(
        headless=True,
        # يمكن إضافة خيارات إضافية لـ Camoufox هنا مثل البروكسي أو البصمة
    ) as browser:
        
        # إنشاء سياق متصفح مع بصمة جهاز حقيقية
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # تحميل الكوكيز (الجلسة) من GitHub Secrets
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم تحميل الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # --- صواريخ السرعة: منع تحميل الموارد الثقيلة (الميزة الكاملة) ---
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            # التوجه للموقع
            print("⏳ جاري فتح Gemini باستخدام المتصفح المخزن...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # البحث عن مربع النص (استخدام الـ Selector الأصلي والمضمون)
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=20000)
            
            # كتابة السؤال والضغط على Enter
            print("✍️ كتابة السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 تم الإرسال، بانتظار الرد...")

            # الانتظار الذكي للرد: انتظار ظهور أزرار التفاعل (دليل اكتمال النص)
            finish_selector = "button[aria-label*='Good response'], button[aria-label*='Share']"
            await page.wait_for_selector(finish_selector, timeout=60000)

            # استخراج النص من آخر رسالة للموديل (Script كامل)
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
            print(f"❌ حدث خطأ: {str(e)}")
            # أخذ لقطة شاشة للخطأ للمساعدة في التصحيح
            await page.screenshot(path="error_debug.png")
            output = {
                "status": "error",
                "message": str(e)
            }

        # حفظ النتيجة النهائية في ملف JSON
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
    else:
        user_prompt = "Hello"

    asyncio.run(run_gemini_automation(user_prompt))
