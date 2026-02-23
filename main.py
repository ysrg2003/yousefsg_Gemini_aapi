import asyncio
import sys
import json
import os
import shutil
import zipfile

# --- 1. منطق فك الضغط الذكي ---
current_dir = os.getcwd()
zip_path = os.path.join(current_dir, "vendor_assets.zip")
# نستخدم مجلد واحد موحد للعمل
extract_path = os.path.join(current_dir, "vendor_extracted")

if os.path.exists(zip_path) and not os.path.exists(extract_path):
    print("📦 جاري فك ضغط المحرك الدائم (Libraries & Browsers)...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# --- 2. إعداد المسارات الموحدة (هام جداً) ---
# نوجه بايثون للمجلد الذي فككنا فيه الضغط للتو
vendor_python = os.path.join(extract_path, "python")
sys.path.insert(0, vendor_python)

# نوجه Playwright للمتصفح داخل المجلد المفكوك
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")

# --- 3. الآن الاستيراد الآمن ---
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم تحميل محرك Camoufox بنجاح.")
except ImportError:
    print("❌ خطأ: فشل الوصول للمكتبات. تأكد من وجود ملف vendor_assets.zip.")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

async def run_gemini_automation(prompt):
    print(f"🚀 بدء العملية... السؤال: {prompt}")
    
    # تشغيل متصفح Camoufox بكامل إعدادات التخفي
    async with AsyncCamoufox(headless=True) as browser:
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # تحميل الكوكيز (الجلسة) إذا وجدت
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم تحميل الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # صواريخ السرعة: منع الموارد الثقيلة
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري فتح Gemini باستخدام البيئة الدائمة...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=20000)
            
            print("✍️ كتابة السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 تم الإرسال، بانتظار الرد...")

            # الانتظار حتى ظهور أزرار التفاعل كدليل على اكتمال النص
            finish_selector = "button[aria-label*='Good response'], button[aria-label*='Share']"
            await page.wait_for_selector(finish_selector, timeout=60000)

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
            await page.screenshot(path="error_debug.png")
            output = {"status": "error", "message": str(e)}

        # حفظ النتيجة في ملف JSON
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello"
    asyncio.run(run_gemini_automation(user_prompt))
