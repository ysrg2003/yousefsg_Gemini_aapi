import os
import sys
import json
import asyncio

# ==========================================================
# 1. إعداد البيئة (يجب أن يتم قبل أي استيراد للمكتبات)
# ==========================================================
extract_path = os.path.join(os.getcwd(), "vendor_extracted")

# تعيين المسارات في بيئة النظام فوراً
os.environ["CAMOUFOX_CACHE_DIR"] = os.path.join(extract_path, "camoufox_cache")
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(extract_path, "browsers")

# إضافة مسار المكتبات البرمجية
vendor_python = os.path.join(extract_path, "python")
sys.path.insert(0, vendor_python)

# ==========================================================
# 2. الاستيراد بعد إعداد المسارات
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("🚀 المحرك جاهز: تم تفعيل وضع الطيران المحلي (Offline Engine).")
except ImportError:
    print("❌ خطأ: لم يتم العثور على مكتبة Camoufox في المسار المحدد.")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 3. محرك الأتمتة
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🧐 الطلب: {prompt}")
    
    # إصلاح الأخطاء في استدعاء المحرك
    try:
        async with AsyncCamoufox(
            headless=True,
            block_images=True,
            # هذا الخيار لإيقاف تحذير الـ LeakWarning الذي ظهر لك
            i_know_what_im_doing=True 
        ) as browser:
            
            # ملاحظة: تم حذف block_fonts لأنه غير مدعوم هنا ويسبب الخطأ
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            )

            cookies_json = os.getenv("GEMINI_COOKIES")
            if cookies_json:
                try:
                    await context.add_cookies(json.loads(cookies_json))
                    print("🔑 تم استعادة الجلسة.")
                except:
                    print("⚠️ فشل حقن الكوكيز.")

            page = await context.new_page()
            
            print("🌐 الإبحار إلى Gemini...")
            await page.goto(GEMINI_URL, wait_until="commit", timeout=60000)

            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ إرسال السؤال...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 بانتظار الرد...")
            response_selector = ".model-response-text"
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_count = 0
            
            for _ in range(60): 
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
                
                if stable_count >= 4:
                    break
                await asyncio.sleep(1)

            final_res = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll("{response_selector}");
                return els.length > 0 ? els[els.length - 1].innerText : "لم يتم استخراج رد.";
            }}''')

            output = {"status": "success", "response": final_res}

    except Exception as e:
        print(f"❌ خطأ تقني: {e}")
        output = {"status": "error", "message": str(e)}

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("💾 تم حفظ النتيجة في result.json")

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello"
    asyncio.run(run_gemini_automation(user_prompt))
