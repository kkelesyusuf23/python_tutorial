from transformers import pipeline

print("🧠 NLP Duygu Analizi Modeli İndiriliyor/Yükleniyor (HuggingFace)...")
print("⚠️ (İlk çalışmada modelin indirilmesi birkaç saniye sürebilir)\n")

# 1. HUGGINGFACE SİHRİ: Duygu Analizi Modelini Çağırıyoruz
# Biz özel bir model belirtmediğimiz için otomatik olarak varsayılan "DistilBERT" modelini indirip kullanacaktır.
duygu_analizoru = pipeline("sentiment-analysis")

# 2. VERİ GİRİŞİ: Borsa, teknoloji ve müşteri yorumlarını simüle eden metin listesi
# Not: Açık kaynak global NLP modellerinin %99'u İngilizce eğitildiği için metinleri İngilizce verdik.
haberler_ve_yorumlar = [
    "I absolutely love the new iPhone! The camera is fantastic and the battery life is great.", 
    "Tesla's stock crashed terribly today. Investors are very panicked and angry.", 
    "The food at that restaurant was okay, but the service was extremely slow and rude.",
    "This is a total scam. Do not buy this product, it broke in two days!"
]

print("📊 Metinlerin İçindeki Duygular Hisse/PR Analizi İçin Taranıyor...\n")

# 3. YAPAY ZEKA (NLP) ANALİZİ
for metin in haberler_ve_yorumlar:
    # Yapay zeka metni okur ve 'POSITIVE' veya 'NEGATIVE' olarak etiketler
    sonuc = duygu_analizoru(metin)[0] 
    
    duygu = sonuc['label']  # POSITIVE veya NEGATIVE
    oran = round(sonuc['score'] * 100, 2) # % olarak güven skoru
    
    # Ekrana renkli ve anlaşılır şekilde bas
    ikon = "✅ OLUMLU (POSITIVE)" if duygu == "POSITIVE" else "❌ OLUMSUZ (NEGATIVE)"
    
    print(f"💬 Metin: '{metin}'")
    print(f"🤖 Yapay Zeka Hissi: {ikon} (Eminlik: %{oran})")
    print("-" * 60)

print("\n🚀 İşlem Tamam! Borsa botlarının veya şirket yöneticilerinin milyonlarca tweeti/haberi nasıl okuduğunu başarmış oldun.")
 