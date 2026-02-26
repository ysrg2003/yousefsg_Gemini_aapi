import asyncio
import sys
import json
import os
import stat

import asyncio
import sys
import json
import os
import stat

# ==========================================================
# 1. تكوين المسارات الذكية (السرعة القصوى)
# ==========================================================
extract_path = os.path.join(os.getcwd(), "vendor_extracted")
vendor_python = os.path.join(extract_path, "python")

# --- التعديل السحري هنا ---
# نخبر Camoufox أن يبحث عن محرك المتصفح داخل المجلد المستخرج بدلاً من تحميله
os.environ["CAMOUFOX_CACHE_DIR"] = os.path.join(extract_path, "camoufox_cache")
# إعداد مسارات Playwright والمكتبات
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")
sys.path.insert(0, vendor_python)

# ==========================================================
# 2. الاستيراد الآمن (بعد إعداد البيئة)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("🚀 المحرك جاهز: تم تفعيل نظام الكاش المحلي (No Download Mode).")
except ImportError as e:
    print(f"❌ خطأ: المكتبات مفقودة في 'vendor_extracted'.\n{e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"


# ==========================================================
# 3. محرك الأتمتة (The Core Engine)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🧐 معالجة الطلب: {prompt}")
    
    # استخدام محرك Camoufox المتخفي
    async with AsyncCamoufox(headless=True) as browser:
        
        # إعداد السياق مع بصمة متصفح واقعية
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        # حقن الكوكيز لتجاوز تسجيل الدخول
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("🔑 تم حقن الجلسة بنجاح.")
            except Exception as e:
                print(f"⚠️ تحذير: فشل حقن الكوكيز ({e})")

        page = await context.new_page()

        # تسريع التصفح: حظر الوسائط الثقيلة
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("🌐 الإبحار إلى Gemini...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # تحديد مربع الإدخال
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ إرسال السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            # --- مراقبة استجابة Gemini (Streaming Monitor) ---
            print("📡 بانتظار توليد الرد...")
            response_selector = ".model-response-text"
            
            # الانتظار حتى يبدأ النص بالظهور
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_count = 0
            
            # فحص نمو النص كل ثانيتين
            for _ in range(45): # حد أقصى 90 ثانية
                current_text = await page.evaluate(f'''() => {{
                    const els = document.querySelectorAll("{response_selector}");
                    return els.length > 0 ? els[els.length - 1].innerText : "";
                }}''')
                
                current_length = len(current_text)
                
                if current_length > previous_length:
                    print(f"✍️ جاري الكتابة... ({current_length} حرف)")
                    # تمرير تلقائي لملاحقة النص
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    previous_length = current_length
                    stable_count = 0
                elif current_length > 0:
                    stable_count += 1
                
                # إذا استقر النص لـ 3 فحوصات (6 ثوانٍ) نعتبره انتهى
                if stable_count >= 3:
                    print("✅ اكتمل الرد.")
                    break
                
                await asyncio.sleep(2)

            # استخراج النتيجة النهائية
            final_res = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll("{response_selector}");
                return els.length > 0 ? els[els.length - 1].innerText : "تعذر استخراج النص.";
            }}''')

            output = {
                "status": "success",
                "prompt": prompt,
                "response": final_res
            }

        except Exception as e:
            print(f"❌ خطأ أثناء التشغيل: {e}")
            await page.screenshot(path="error_debug.png") # لقطة شاشة للديبريس!
            output = {"status": "error", "message": str(e)}

        # حفظ النتيجة في ملف JSON
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print("💾 تم حفظ النتيجة في result.json")

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello Gemini"
    asyncio.run(run_gemini_automation(user_prompt))
