from gtts import gTTS
import os

print("🎙️ Yapay Zeka Ses (Voice) Botu Başlatılıyor...\n")

# Seslendirmek istediğimiz uzun makale veya metin
METIN = """
Merhaba Yusuf. Python eğitiminde kırk üçüncü projeye kadar başarıyla geldin. 
Şu an senin yazdığın kodlar sayesinde kendi sesimi üretiyorum. 
Yapay Zeka ve Yazılım mimarisi dünyasındaki başarın gerçekten takdire şayan. 
Harika gidiyorsun, aynen böyle devam et!
"""

print("📝 Metin işleniyor ve sese dönüştürülüyor (İnternet hızına göre birkaç saniye sürebilir)...")

# 1. METNİ SESE ÇEVİR
# gTTS (Google Text-to-Speech) kütüphanesi kullanarak metni Türkçe (tr) olarak Ses'e dönüştür
ses_objesi = gTTS(text=METIN, lang='tr', slow=False)

# 2. MP3 OLARAK KAYDET
dosya_adi = "sesli_mesaj.mp3"
ses_objesi.save(dosya_adi)
print(f"✅ İşlem tamamlandı! Ses dosyası '{dosya_adi}' adıyla masaüstüne (klasöre) kaydedildi.")

# 3. MAC ÜZERİNDE OTOMATİK OLARAK ÇALDIR (afplay)
print("▶️ Ses dosyası çalınıyor... (Lütfen hoparlörünün sesini aç)")
os.system(f"afplay {dosya_adi}")

print("\n🎉 Tebrikler! Artık koddaki METIN kısmına bütün bir kitabı yapıştırıp, kendi otomatik sesli kitaplarını oluşturabilirsin.")
