import asyncio
import sys
import json
from camoufox.async_api import AsyncCamoufox

async def run_gemini(prompt):
    # إعدادات Camoufox لمحاكاة متصفح حقيقي (بصمة إصبع عشوائية ولكن بشرية)
    async with AsyncCamoufox(headless=True) as browser:
        # إنشاء سياق متصفح مع إعدادات تخفي عالية
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print(f"🚀 البدء: التوجه إلى Gemini لإرسال: {prompt}")
        
        try:
            # 1. الدخول للموقع
            await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=60000)
            
            # 2. البحث عن مربع النص (Selector الخاص بـ Gemini الرسمي)
            # نستخدم Selector مرن لأن Google تغير الأسماء أحياناً
            input_selector = "div[role='textbox'], textarea[aria-label]"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            # 3. محاكاة الكتابة البشرية (تأخير بسيط بين الحروف للتخفي)
            await page.type(input_selector, prompt, delay=50)
            await page.keyboard.press("Enter")
            
            print("⏳ تم الإرسال، بانتظار توليد الرد...")

            # 4. انتظار انتهاء الرد 
            # العلامة هي اختفاء زر "إيقاف التوليد" أو ظهور أزرار التفاعل (Like/Dislike)
            await asyncio.sleep(5) # انتظار أولي
            await page.wait_for_selector("button[aria-label*='Good response'], .model-response-text", timeout=60000)

            # 5. استخراج النص
            # نأخذ آخر رسالة من الـ Model
            responses = await page.query_selector_all(".model-response-text")
            if responses:
                final_text = await responses[-1].inner_text()
            else:
                # محاولة استخراج بطريقة بديلة إذا تغير الـ CSS
                final_text = await page.evaluate("() => document.querySelector('.model-response-text').innerText")

            # حفظ النتيجة في ملف JSON ليسهل قراءتها برمجياً
            output = {"status": "success", "response": final_text}
            
        except Exception as e:
            output = {"status": "error", "message": str(e)}

        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        
        print("✅ تم استخراج الرد بنجاح.")

if __name__ == "__main__":
    user_input = sys.argv[1] if len(sys.argv) > 1 else "Hello Gemini"
    asyncio.run(run_gemini(user_input))
