import os
import sys
import json
import asyncio

# استيراد محرك Camoufox
try:
    from camoufox.async_api import AsyncCamoufox
    print("🚀 المحرك جاهز: تم تفعيل البيئة المحلية بنجاح.")
except ImportError:
    print("❌ خطأ: لم يتم العثور على مكتبة Camoufox. تحقق من إعداد PYTHONPATH.")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

async def run_gemini_automation(prompt):
    print(f"🧐 الطلب المستلم: {prompt}")
    
    output = {"status": "error", "message": "فشل التشغيل المبدئي"}

    try:
        # تشغيل المحرك (سيستخدم الكاش الموجود في /home/runner/.cache/camoufox تلقائياً)
        async with AsyncCamoufox(
            headless=True,
            block_images=True,
            i_know_what_im_doing=True,  # ضروري لتجنب تحذيرات الـ WAF
            addons=[],
            humanize=False,
        ) as browser:
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            )

            # استعادة الجلسة عبر الكوكيز
            cookies_json = os.getenv("GEMINI_COOKIES")
            if cookies_json:
                try:
                    await context.add_cookies(json.loads(cookies_json))
                    print("🔑 تم حقن كوكيز الجلسة.")
                except Exception as e:
                    print(f"⚠️ فشل حقن الكوكيز: {e}")

            page = await context.new_page()
            
            print("🌐 الإبحار إلى Gemini...")
            # استخدام domcontentloaded لتسريع الدخول
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # تحديد مربع النص (يدعم عدة اختيارات لضمان الوصول)
            input_selector = "div[role='textbox'], [contenteditable='true'], #input-area"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ إرسال السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            # --- مراقبة استقرار الرد ---
            print("📡 بانتظار رد الذكاء الاصطناعي...")
            response_selector = ".model-response-text"
            
            # الانتظار حتى يبدأ النص بالظهور
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_count = 0
            
            # فحص استقرار النص (Loop لمدة 90 ثانية كحد أقصى)
            for _ in range(90): 
                current_text = await page.evaluate(f'''() => {{
                    const els = document.querySelectorAll("{response_selector}");
                    return els.length > 0 ? els[els.length - 1].innerText : "";
                }}''')
                
                current_length = len(current_text)
                
                if current_length > previous_length:
                    previous_length = current_length
                    stable_count = 0
                elif current_length > 0:
                    stable_count += 1
                
                # إذا استقر النص لـ 4 ثوانٍ متتالية نعتبره انتهى
                if stable_count >= 4:
                    print(f"✅ اكتمل استخراج الرد بنجاح.")
                    break
                
                await asyncio.sleep(1)

            # جلب النتيجة النهائية
            final_res = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll("{response_selector}");
                return els.length > 0 ? els[els.length - 1].innerText : "فشل استخراج نص الرد.";
            }}''')

            output = {"status": "success", "response": final_res}

    except Exception as e:
        print(f"❌ خطأ تقني: {e}")
        output = {"status": "error", "message": str(e)}

    # حفظ النتيجة في ملف JSON
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("💾 تم حفظ النتيجة في result.json")

if __name__ == "__main__":
    # الحصول على السؤال من سطر الأوامر
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello"
    asyncio.run(run_gemini_automation(user_prompt))
