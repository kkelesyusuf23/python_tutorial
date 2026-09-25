import requests
from bs4 import BeautifulSoup
from transformers import pipeline

print("📰 AI Haber Bülteni Robotu Başlatılıyor...")
print("⚠️ (İlk çalışmada AI Özetleme Modeli ineceği için biraz sürebilir)\n")

# 1. YAPAY ZEKA MODELİNİ YÜKLE (HuggingFace Summarization)
# sshleifer/distilbart-cnn modeli uzun metinleri kısaltmak için eğitilmiştir.
ozetleyici = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# 2. WEB SCRAPING: HackerNews sitesine sız ve haberleri topla
print("🕵️‍♂️ HackerNews web sitesi taranıyor...")
url = "https://news.ycombinator.com/"
# Robot olmadığımızı kanıtlamak için basit bir User-Agent maskesi
headers = {'User-Agent': 'Mozilla/5.0'}
cevap = requests.get(url, headers=headers)
corba = BeautifulSoup(cevap.text, "html.parser")

# Sitedeki ilk 3 haberin başlığını (class_="titleline") alıyoruz
haber_satirlari = corba.find_all("span", class_="titleline")[:3]
haberler = [satir.a.text for satir in haber_satirlari]

print(f"✅ {len(haberler)} adet haber başarıyla çekildi. AI Özetlemeye geçiriliyor...\n")
print("=" * 60)
print("☕ GÜNLÜK SABAH BÜLTENİNİZ")
print("=" * 60)

# 3. AI ÖZETLEME (Bülten Hazırlığı)
for i, baslik in enumerate(haberler, 1):
    print(f"📰 HABER BAŞLIĞI: {baslik}")
    
    # Normalde buraya haberin uzun detay metnini veririz (Linke tıklayıp kazıyarak).
    # Örnek olması açısından başlığı uzun bir metinmiş gibi Yapay Zekaya veriyoruz.
    # Model, bu metni okuyup en önemli cümleyi (Özeti) çıkaracaktır.
    uzun_metin = baslik + " This is an important breaking news story from the tech world today. Investors and tech enthusiasts are watching closely."
    
    # Yapay zekadan en fazla 20 kelimelik kısa bir özet (bullet point) istiyoruz
    ozet = ozetleyici(uzun_metin, max_length=20, min_length=5, do_sample=False)[0]['summary_text']
    
    print(f"🤖 AI ÖZETİ: {ozet.strip()}")
    print("-" * 60)
    
print("\n🚀 İşlem Tamam! Kendi bülten otomasyonunu yazdın. İstersen bunu maile çevirip her sabah kendine attırabilirsin.")
