import asyncio
import sys
import json
import os
from camoufox.async_api import AsyncCamoufox

# إعدادات اختيارية: استخراج النص البرمجي
# إذا كنت تريد تشغيل الكوكيز، ضعها في متغير بيئة باسم GEMINI_COOKIES
GEMINI_URL = "https://gemini.google.com/app"

async def run_gemini_automation(prompt):
    print(f"🚀 بدء العملية... السؤال: {prompt}")
    
    # تشغيل متصفح Camoufox بإعدادات التخفي
    async with AsyncCamoufox(headless=True) as browser:
        # إنشاء سياق متصفح جديد
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # تحميل الكوكيز إذا وجدت لتجاوز تسجيل الدخول
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم تحميل الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # --- صواريخ السرعة: منع تحميل الموارد الثقيلة ---
        # سنمنع الصور، الخطوط، والستايلات غير الضرورية لتسريع التحميل بنسبة 300%
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            # التوجه للموقع - ننتظر فقط حتى يتم تحميل هيكل الصفحة الأساسي
            print("⏳ جاري فتح Gemini...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # البحث عن مربع النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=20000)
            
            # كتابة السؤال والضغط على Enter
            print("✍️ كتابة السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 تم الإرسال، بانتظار الرد...")

            # الانتظار الذكي للرد:
            # ننتظر حتى تظهر أزرار التفاعل (مثل زر الإعجاب أو المشاركة) 
            # لأنها لا تظهر إلا بعد اكتمال توليد النص بالكامل.
            finish_selector = "button[aria-label*='Good response'], button[aria-label*='Share']"
            await page.wait_for_selector(finish_selector, timeout=60000)

            # استخراج النص من آخر رسالة للموديل
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
            # أخذ لقطة شاشة للخطأ للمساعدة في التصحيح داخل GitHub Actions
            await page.screenshot(path="error_debug.png")
            output = {
                "status": "error",
                "message": str(e)
            }

        # حفظ النتيجة النهائية في ملف JSON
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # الحصول على البرومبت من سطر الأوامر
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
    else:
        user_prompt = "Hello, who are you?"

    asyncio.run(run_gemini_automation(user_prompt))
