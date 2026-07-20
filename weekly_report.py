import os
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

# استدعاء دالة الاتصال بشيت جوجل من ملفاتك
from gsheets import get_results_sheet #[cite: 2]

# إعدادات الإيميل الخاصة بك والموجودة في النظام
SMTP_SERVER = "smtp.gmail.com" #[cite: 1]
SMTP_PORT = 465 #[cite: 1]
SENDER_EMAIL = "ahmedrefat86@gmail.com" #[cite: 1]
SENDER_PASSWORD = "wbkc fyun luvb tdtl" #[cite: 1]
# قم بتغيير هذا الإيميل إلى إيميل صاحب الشركة
OWNER_EMAIL = "hashem.saad@lotuspharmacies.com" 

def send_weekly_report():
    print("بدء تجهيز التقرير الأسبوعي...")
    
    # 1. سحب البيانات من Google Sheets
    try:
        sheet = get_results_sheet() #[cite: 2]
        records = sheet.get_all_records()
    except Exception as e:
        print(f"خطأ في الاتصال بجوجل شيت: {e}")
        return

    if not records:
        print("لا توجد بيانات لإرسالها.")
        return

    df = pd.DataFrame(records)
    
    # 2. فلترة البيانات لآخر أسبوع فقط
    # تحويل عمود التاريخ إلى صيغة datetime لسهولة المقارنة
    df['Exam Date'] = pd.to_datetime(df['Exam Date'])
    last_week = datetime.now() - timedelta(days=7)
    
    # استخراج امتحانات آخر 7 أيام
    weekly_data = df[df['Exam Date'] >= last_week]
    
    if weekly_data.empty:
        print("لا توجد امتحانات تم إجراؤها هذا الأسبوع.")
        return

    # 3. إعداد إحصائيات التقرير
    total_exams = len(weekly_data)
    # تنظيف البيانات للعرض في الإكسيل (اختياري)
    weekly_data['Exam Date'] = weekly_data['Exam Date'].dt.strftime('%Y-%m-%d %H:%M')
    
    # 4. حفظ البيانات في ملف Excel مؤقت
    report_filename = f"Weekly_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    weekly_data.to_excel(report_filename, index=False, engine='openpyxl')

    # 5. تجهيز الإيميل
    msg = EmailMessage()
    msg["Subject"] = f"📊 التقرير الأسبوعي لنتائج الامتحانات - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = SENDER_EMAIL #[cite: 1]
    msg["To"] = OWNER_EMAIL

    # محتوى الرسالة
    msg.set_content(f"""
أهلاً بك،

مرفق طيه التقرير الأسبوعي لنتائج امتحانات التقييم والتوظيف.

📌 ملخص هذا الأسبوع:
- إجمالي عدد الامتحانات المجراة: {total_exams} امتحان.

برجاء الاطلاع على ملف الإكسيل المرفق لمعرفة أسماء الممتحنين، التقييمات، وتفاصيل النتائج (الإجابات الصحيحة والخاطئة والوقت المستغرق).

تحياتي،
نظام الامتحانات الآلي
""")

    # إرفاق الملف
    with open(report_filename, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=report_filename,
        )

    # 6. إرسال الإيميل
    try:
        # استخدام SMTP_SSL كحل جذري لمشاكل الإرسال 
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server: #[cite: 1]
            server.login(SENDER_EMAIL, SENDER_PASSWORD) #[cite: 1]
            server.send_message(msg)
        print("✅ تم إرسال التقرير الأسبوعي بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الإرسال: {e}")
    finally:
        # مسح ملف الإكسيل بعد الإرسال لتنظيف مساحة السيرفر
        if os.path.exists(report_filename):
            os.remove(report_filename)

if __name__ == "__main__":
    send_weekly_report()