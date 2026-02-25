
# 🚀 Gemini AAPI Pro: البنية التحتية المتكاملة لأتمتة ذكاء Gemini الاصطناعي

**Gemini AAPI Pro** هو نظام هجين (Hybrid System) مصمم ليكون بديلاً سيادياً ومجانياً بالكامل للـ API الرسمي الخاص بـ Google Gemini. يعتمد المشروع على تقنيات أتمتة المتصفح (Browser Automation) عبر سحابة GitHub Actions لتشغيل أحدث نماذج Gemini (بما فيها نماذج Flash المحدثة) دون قيود مادية أو جغرافية.

---

## 🛠️ المميزات التقنية (Key Features)

* **Zero-Cost Infrastructure:** استغلال موارد GitHub Actions المجانية (2000 دقيقة شهرياً).
* **Anti-Bot Stealth Engine:** استخدام محرك `Camoufox` المدمج مع `Playwright` لتجاوز أنظمة كشف البوتات (Bypass Google/Cloudflare Defense).
* **No Rate Limits:** تجاوز القيود الصارمة المفروضة على عدد الرموز (Tokens) في النسخ المجانية للـ API الرسمي.
* **Seamless Integration:** دعم كامل للربط مع n8n، تطبيقات Web، وبوتات التواصل الاجتماعي.
* **Asynchronous Processing:** معالجة الطلبات في بيئات منعزلة (Isolated Environments) لضمان الأمان والخصوصية.

---

## 🏗️ هيكلية النظام (System Architecture)

يعمل النظام عبر دورة حياة تقنية مكونة من 4 مراحل:
1.  **Request Phase:** إرسال طلب `workflow_dispatch` عبر GitHub API.
2.  **Execution Phase:** تشغيل حاوية Ubuntu سحابية، فك ضغط بيئة العمل (`vendor_assets.zip`) وتشغيل السكربت.
3.  **Extraction Phase:** محاكاة دخول المستخدم بالـ Cookies، كتابة البرومبت، ومراقبة استقرار الـ DOM لاستخراج الرد.
4.  **Delivery Phase:** رفع النتيجة كـ JSON Artifact مضغوط، متاح للتحميل عبر بروتوكول HTTP.



---

## 📋 المتطلبات (Prerequisites)

لاستخدام هذا النظام، يجب توفير المتطلبات التالية بدقة:

1.  **GitHub PAT (Personal Access Token):** * يجب أن يمتلك صلاحيات `workflow` و `repo`.
    * يُستخدم لتفويض العمليات البرمجية من خارج GitHub.
    * افتح ملف الـ HTML الذي قمت ببرمجته في المتصفح.
في أعلى الصفحة جهة اليسار (أو اليمين حسب لغة المتصفح)، ستجد أيقونة على شكل ترس ⚙️.
اضغط على هذا الترس؛ ستنفتح لك لوحة إعدادات منسدلة باللون الأبيض (أو الأسود في الوضع الليلي).
ستجد خانتين (مربعين نصيين):
الخانة الأولى مكتوب فوقها: GitHub Personal Token.
هنا بالظبط تقوم بلصق الرمز الذي يبدأ بـ ghp_.
الخانة الثانية مكتوب فوقها: المستودع (User/Repo).
تكتب فيها اسم حسابك واسم المشروع، مثل: YourName/YourRepo.
2.  **Gemini Session Cookies:**
    * مطلوب ملف `cookies.json` يحتوي على قيم الجلسة النشطة (`__Secure-1PSID`, `__Secure-1PSIDTS`).
    * يتم استخراجها عبر إضافة **Cookie-Editor** ووضعها داخل المستودع.
3.  **Forking:** * يجب عمل Fork للمستودع إلى حسابك الشخصي لتتمكن من الوصول لنقاط النهاية (Endpoints) الخاصة بالـ API.

---

## 💻 الاستخدام كبديل للـ API (JavaScript Implementation)

يمكنك دمج المنظومة في أي مشروع JavaScript باستخدام الكود التالي كبديل للمكتبات الرسمية:

```javascript
/**
 * محرك استدعاء Gemini AAPI المخصص
 */
const GeminiEngine = {
    config: {
        token: "ghp_YOUR_TOKEN",
        repo: "USER/REPO_NAME",
        workflow: "gemini_api.yml"
    },

    async ask(prompt) {
        // 1. تشغيل الأكشن (Trigger)
        const dispatch = await fetch(`https://api.github.com/repos/${this.config.repo}/actions/workflows/${this.config.workflow}/dispatches`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.config.token}`,
                'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify({ ref: 'main', inputs: { prompt: prompt } })
        });

        if (dispatch.status !== 204) throw new Error("فشل تشغيل محرك الأتمتة");

        // 2. الانتظار (Polling) - يفضل استخدامه مع نظام Promises
        console.log("⏳ الانتظار لمعالجة الطلب سحابياً...");
        return this.fetchResult();
    },

    async fetchResult() {
        // الانتظار 55 ثانية كحد أدنى للمعالجة
        await new Promise(r => setTimeout(r, 55000));
        
        // جلب أحدث ملف Artifact
        const res = await fetch(`https://api.github.com/repos/${this.config.repo}/actions/artifacts?per_page=1`);
        const data = await res.json();
        return data.artifacts[0].archive_download_url;
    }
};
```
🤖 التكامل مع n8n (Workflow Automation)
لتحويل النظام إلى API Server داخل منصة n8n، استخدم الهيكلية التالية:
n8n Workflow JSON (Import Ready)
يتم ربط العقد كالتالي: Chat Trigger -> HTTP Request (Post) -> Wait (50s) -> HTTP Request (Get) -> Extract Zip -> Final Output.
```
{
  "nodes": [
    {
      "parameters": { "options": {} },
      "id": "1", "name": "Chat Trigger", "type": "n8n-nodes-base.chatTrigger", "typeVersion": 1, "position": [100, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "[https://api.github.com/repos/YOUR_REPO/actions/workflows/gemini_api.yml/dispatches](https://api.github.com/repos/YOUR_REPO/actions/workflows/gemini_api.yml/dispatches)",
        "sendHeaders": true,
        "headerParameters": { "parameters": [{ "name": "Authorization", "value": "Bearer YOUR_TOKEN" }] },
        "sendBody": true,
        "bodyParameters": { "parameters": [{ "name": "ref", "value": "main" }, { "name": "inputs", "value": "={{ JSON.stringify({ prompt: $json.chatInput }) }}" }] }
      },
      "id": "2", "name": "GitHub Dispatch", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.1, "position": [320, 200]
    },
    {
      "parameters": { "amount": 55, "unit": "seconds" },
      "id": "3", "name": "Wait for AI", "type": "n8n-nodes-base.wait", "typeVersion": 1, "position": [540, 200]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "[https://api.github.com/repos/YOUR_REPO/actions/artifacts?per_page=1](https://api.github.com/repos/YOUR_REPO/actions/artifacts?per_page=1)",
        "sendHeaders": true,
        "headerParameters": { "parameters": [{ "name": "Authorization", "value": "Bearer YOUR_TOKEN" }] },
        "options": { "response": { "response": { "responseFormat": "file" } } }
      },
      "id": "4", "name": "Download Artifact", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.1, "position": [760, 200]
    }
  ]
}
```

🛡️ بروتوكولات الأمان (Security & Maintenance)
 * Cookies Lifecycle: يجب تحديث ملف الكوكيز دورياً لضمان عدم خروج المتصفح من الجلسة.
 * PAT Expiry: تأكد من تجديد التوكن الخاص بـ GitHub قبل انتهائه لضمان استمرارية الـ API.
 * Artifact Cleanup: يقوم GitHub بحذف الـ Artifacts تلقائياً بعد 90 يوماً، ولكن يفضل حذفها برمجياً لزيادة الخصوصية.
📜 رخصة الاستخدام (License)
هذا المشروع مخصص للأغراض التعليمية والبحثية لتوضيح قدرات أتمتة الويب. يرجى استخدامه بمسؤولية ووفقاً لسياسات الاستخدام الخاصة بـ Google و GitHub.
تطوير: [Ysrg2003]
الحالة: Active / Production Ready

---

**ملاحظة ختامية:** هذا الملف يمثل "الدستور التقني" لمشروعك. لقد وضعت فيه كل الروابط المنطقية بين الأكواد التي ناقشناها، مع توضيح كيفية انتقال البيانات من "دردشة n8n" إلى "سيرفرات GitHub" ثم عودتها كإجابة. هل تريد مني إضافة قسم خاص بـ **Troubleshooting** (حل المشاكل الشائعة) للملف؟

