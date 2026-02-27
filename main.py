import os
import sys
import json
import asyncio

# 1. التحقق من البيئة والمحرك
try:
    from camoufox.async_api import AsyncCamoufox
    print("🚀 المحرك جاهز: تم تفعيل بيئة ChatGPT المتطورة.")
except ImportError:
    print("❌ خطأ: لم يتم العثور على مكتبة Camoufox. تأكد من تثبيتها عبر pip install camoufox.")
    sys.exit(1)

# الإعدادات الأساسية
CHATGPT_URL = "https://chatgpt.com"
# المحددات الخاصة بـ ChatGPT (Selectors)
INPUT_SELECTOR = "#prompt-textarea"
# نختار حاوية الرد الخاصة بالمساعد والتي تحتوي على التنسيق
RESPONSE_SELECTOR = 'div[data-message-author-role="assistant"] .markdown'

async def run_chatgpt_automation(prompt):
    print(f"🧐 جاري معالجة الطلب: {prompt}")
    
    output = {"status": "error", "message": "فشل التشغيل المبدئي"}

    try:
        # 2. إعداد المتصفح بتقنيات تخفي متقدمة
        async with AsyncCamoufox(
            headless=True,            # غيرها لـ False إذا أردت رؤية ما يحدث
            block_images=True,        
            i_know_what_im_doing=True, 
            humanize=True,            
        ) as browser:
            
            # 3. إعداد سياق المتصفح مع User Agent حديث
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            )

            # 4. إدارة الجلسة عبر الكوكيز
            cookies_json = os.getenv("CHATGPT_COOKIES")
            if cookies_json:
                try:
                    await context.add_cookies(json.loads(cookies_json))
                    print("🔑 تم حقن كوكيز الجلسة بنجاح.")
                else:
                    print("⚠️ تحذير: لم يتم العثور على متغير CHATGPT_COOKIES، قد يطلب الموقع تسجيل الدخول.")
                except Exception as e:
                    print(f"⚠️ خطأ في معالجة الكوكيز: {e}")

            page = await context.new_page()
            
            # 5. الدخول إلى الموقع مع آلية إعادة المحاولة (Retry Logic)
            print("🌐 الإبحار إلى ChatGPT...")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await page.goto(CHATGPT_URL, wait_until="networkidle", timeout=60000)
                    # الانتظار للتأكد من تجاوز أي حماية أولية
                    await page.wait_for_selector(INPUT_SELECTOR, timeout=20000)
                    print("✅ تم تحميل واجهة الدردشة بنجاح.")
                    break
                except Exception:
                    if attempt < max_retries - 1:
                        print(f"🔄 محاولة {attempt + 1} فشلت، جاري إعادة المحاولة...")
                        await asyncio.sleep(2)
                    else:
                        await page.screenshot(path="error_timeout.png")
                        raise Exception("فشل الوصول لصندوق الإدخال بعد عدة محاولات. تم حفظ صورة للخطأ.")

            # 6. كتابة السؤال وإرساله (محاكاة بشرية)
            print("✍️ كتابة السؤال وإرساله...")
            await page.fill(INPUT_SELECTOR, prompt)
            await asyncio.sleep(0.5)
            await page.keyboard.press("Enter")
            
            # 7. مراقبة تدفق الرد واستقراره
            print("📡 بانتظار رد الذكاء الاصطناعي...")
            await page.wait_for_selector(RESPONSE_SELECTOR, timeout=60000)
            
            previous_html = ""
            stable_count = 0
            
            # فحص استقرار الرد (تعديل لسرعة ChatGPT)
            for _ in range(120): # حد أقصى دقيقتين للردود الطويلة
                current_html = await page.evaluate(f'''() => {{
                    const els = document.querySelectorAll('{RESPONSE_SELECTOR}');
                    return els.length > 0 ? els[els.length - 1].innerHTML : "";
                }}''')
                
                if len(current_html) > len(previous_html):
                    previous_html = current_html
                    stable_count = 0
                elif len(current_html) > 0:
                    stable_count += 1
                
                # إذا استقر الرد لـ 6 ثوانٍ، نعتبره اكتمل
                if stable_count >= 6:
                    print(f"✅ تم التقاط الرد المنسق بالكامل.")
                    break
                
                await asyncio.sleep(1)

            # 8. استخراج النتيجة النهائية
            final_res_html = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll('{RESPONSE_SELECTOR}');
                if (els.length > 0) {{
                    return els[els.length - 1].innerHTML; 
                }}
                return "خطأ: لم نتمكن من العثور على محتوى الرد.";
            }}''')

            output = {"status": "success", "response": final_res_html}

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")
        output = {"status": "error", "message": str(e)}

    # 9. حفظ النتيجة النهائية
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("💾 تم حفظ الرد في result.json")

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "اكتب ٢ كود بايثون و ٢ كود js مع شرح كل منهم وجدول مقارنة بين اللغتين"
    asyncio.run(run_chatgpt_automation(user_prompt))
