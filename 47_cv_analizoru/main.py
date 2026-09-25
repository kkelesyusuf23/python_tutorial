import json
import time

print("🤖 İK Yapay Zeka (ATS) Botu Başlatılıyor...\n")

# 1. PROMPT ENGINEERING (İstem Mühendisliği)
# Yapay Zekaya (GPT) vereceğimiz 'Rol' ve kurallar bütünü. (Buna System Prompt denir)
SYSTEM_PROMPT = """
Sen çok uluslu bir teknoloji şirketinde çalışan, son derece acımasız ve seçici bir İnsan Kaynakları Müdürüsün.
Sana verilen CV metnini analiz edeceksin.
Adayı şu 3 kritere göre değerlendireceksin:
1. Güçlü Yönler
2. Zayıf Yönler
3. ATS Puanı (100 üzerinden bir sayı)

Cevabını sadece JSON formatında döndür.
Örnek Format:
{
    "puan": 75,
    "guclu_yonler": "Python biliyor",
    "zayif_yonler": "Staj tecrübesi yok"
}
"""

# 2. ÖRNEK ADAYIN CV'Sİ
ORNEK_CV = """
Adı: Ali Yılmaz
Eğitim: X Üniversitesi Bilgisayar Mühendisliği (2020 Mezunu)
Deneyim: Yok
Yetenekler: Python, HTML, CSS, biraz JavaScript.
Hobiler: Oyun oynamak, kitap okumak.
İngilizce Seviyesi: Başlangıç (A2)
"""

print("📝 Adayın CV'si okunuyor...")
print("-" * 50)
print(ORNEK_CV)
print("-" * 50)

print("🧠 Yapay Zeka (OpenAI) Analiz Ediyor... Lütfen bekleyin.\n")
time.sleep(2) # Gerçek API isteğini (2 saniye) simüle ediyoruz

# 3. OPENAI API BAĞLANTISI (Gerçek Mimarinin Simülasyonu)
# İleride kendi OpenAI API Key'ini buraya girerek gerçek GPT-4 modelini çalıştırabilirsin.
"""
from openai import OpenAI
client = OpenAI(api_key="SENIN_API_ANAHTARIN")

cevap = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": ORNEK_CV}
    ]
)
ai_yaniti = json.loads(cevap.choices[0].message.content)
"""

# Simüle edilmiş (Mock) AI Yanıtı (Gerçek OpenAI çıktısının birebir aynısı)
ai_yaniti = {
    "puan": 45,
    "guclu_yonler": "Bilgisayar mühendisliği alanında lisans diploması var. Temel web teknolojilerini (HTML, CSS) ve Python dilini biliyor.",
    "zayif_yonler": "Hiçbir profesyonel veya staj deneyimi yok. Global bir teknoloji şirketi için İngilizce seviyesi (A2) çok yetersiz. Sadece 'biraz' JavaScript bilmesi günümüz modern framework (React vb.) standartlarını karşılamıyor."
}

# 4. SONUÇLARIN YAZDIRILMASI
print("--- 👔 ATS (YAPAY ZEKA) İK RAPORU ---")
print(f"📊 Adayın Puanı: {ai_yaniti['puan']} / 100")

# 60 puan altı elenir
if ai_yaniti['puan'] >= 60:
    print("✅ DURUM: Aday Mülakata Çağrıldı!")
else:
    print("❌ DURUM: Aday İlk Aşamada (Yapay Zeka Tarafından) Elendi.")

print("\n💪 Güçlü Yönleri:")
print(f"- {ai_yaniti['guclu_yonler']}")

print("\n⚠️ Zayıf Yönleri:")
print(f"- {ai_yaniti['zayif_yonler']}")
print("-------------------------------------")

print("\n🚀 İşlem Tamam! Artık Prompt Engineering kullanarak yapay zekaya dilediğin karakteri (Rolü) verebilirsin.")
