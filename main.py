import os
import sys
import json
import asyncio

# ==========================================================
# 1. إعداد المسارات البرمجية (للمكتبات المستخرجة فقط)
# ==========================================================
# إضافة مجلد المكتبات الحالي إلى المسار لضمان عمل الاستيراد
sys.path.insert(0, os.getcwd())

try:
    from camoufox.async_api import AsyncCamoufox
    print("🚀 المحرك جاهز: وضع التشغيل المحلي مفعل.")
except ImportError:
    print("❌ خطأ: مكتبة Camoufox غير موجودة. تأكد من خطوة Unzip في الـ YAML.")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 2. محرك الأتمتة الأساسي
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🧐 الطلب: {prompt}")
    
    # مصفوفة النتيجة الافتراضية
    output = {"status": "error", "message": "لم يبدأ التنفيذ"}

    try:
        # تشغيل المحرك بأقل استهلاك للموارد وبدون تحميل خارجي
        async with AsyncCamoufox(
            headless=True,
            block_images=True,
            i_know_what_im_doing=True  # لتجاوز تحذيرات الـ WAF والـ Leak
        ) as browser:
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )

            # حقن الجلسة (Cookies)
            cookies_json = os.getenv("GEMINI_COOKIES")
            if cookies_json:
                try:
                    await context.add_cookies(json.loads(cookies_json))
                    print("🔑 تم استعادة الجلسة بنجاح.")
                except Exception as e:
                    print(f"⚠️ تحذير الكوكيز: {e}")

            page = await context.new_page()
            
            print("🌐 الدخول إلى Gemini...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # انتظر مربع النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ كتابة السؤال وإرساله...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            # --- نظام مراقبة الرد الذكي ---
            print("📡 بانتظار استقرار الرد...")
            response_selector = ".model-response-text"
            
            # الانتظار الأولي لظهور أي جزء من الرد
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_count = 0
            
            # حلقة فحص نمو النص (كل 1 ثانية)
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
                
                # إذا لم يتغير حجم النص لمدة 4 ثوانٍ، نعتبره انتهى
                if stable_count >= 4:
                    print(f"✅ انتهى Gemini من الكتابة.")
                    break
                
                await asyncio.sleep(1)

            # جلب النص النهائي
            final_res = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll("{response_selector}");
                return els.length > 0 ? els[els.length - 1].innerText : "فشل في استخراج النص.";
            }}''')

            output = {"status": "success", "response": final_res}

    except Exception as e:
        print(f"❌ خطأ تقني أثناء التشغيل: {e}")
        output = {"status": "error", "message": str(e)}

    # حفظ النتيجة النهائية مهما كانت الظروف
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("💾 تم تحديث result.json")

if __name__ == "__main__":
    # استلام السؤال من الـ Workflow
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello"
    asyncio.run(run_gemini_automation(user_prompt))
