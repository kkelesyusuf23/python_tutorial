import os
import subprocess

print("🤖 Kendi 'Antigravity' (Agentic AI) Asistanımız Başlatılıyor...\n")

# ================= 1. YETENEKLER (TOOLS / FUNCTIONS) =================
# Yapay Zekaya kullanabileceği "Fiziksel Araçları (Tool)" tanımlıyoruz.
# Gerçek dünyada bir LLM'e (GPT-4) sadece konuşmayı değil, bu fonksiyonları çağırma yetkisi verilir.

def klasor_olustur(klasor_adi):
    print(f"   🔧 ARAÇ TETİKLENDİ (Tool Called): '{klasor_adi}' adında klasör açılıyor...")
    os.makedirs(klasor_adi, exist_ok=True)
    return f"Klasör '{klasor_adi}' başarıyla oluşturuldu."

def dosyaya_yaz(dosya_adi, icerik):
    print(f"   🔧 ARAÇ TETİKLENDİ (Tool Called): '{dosya_adi}' dosyasına yazı yazılıyor...")
    with open(dosya_adi, "w") as f:
        f.write(icerik)
    return f"'{dosya_adi}' oluşturuldu ve metin içine kaydedildi."

def sistemi_dinle(komut):
    print(f"   🔧 ARAÇ TETİKLENDİ (Tool Called): Sistemde '{komut}' komutu çalıştırılıyor...")
    # Mac/Linux komutlarını (Örn: ls, date) çalıştırır ve çıktıyı çeker
    sonuc = subprocess.check_output(komut, shell=True, text=True)
    return sonuc.strip()


# ================= 2. YAPAY ZEKA (LLM) BEYNİ =================
# Kullanıcıdan gelen "İngilizce/Türkçe" cümleyi anlar ve hangi Aracı (Tool) çalıştıracağına KARAR VERİR.
def ai_ajani(kullanici_istegi):
    print(f"🗣️ KULLANICI İSTEĞİ: '{kullanici_istegi}'")
    print("🧠 YAPAY ZEKA: Düşünüyorum... Hangi aracı (Tool) kullanmalıyım?\n")
    
    istek = kullanici_istegi.lower()
    
    # NLP / Tool Calling Mantığı (LLM'ler arka planda bunu JSON formatında karar verir)
    if "klasör" in istek and ("aç" in istek or "oluştur" in istek):
        # AI Kararı: klasor_olustur aracını çağır
        sonuc = klasor_olustur("agent_klasoru")
    
    elif "dosya" in istek and "yaz" in istek:
        # AI Kararı: dosyaya_yaz aracını çağır
        sonuc = dosyaya_yaz("veda_mektubu.txt", "Tebrikler Yusuf! 50 Projelik Ustalık Eğitimini tamamladın. \nSevgiler, Antigravity.")
        
    elif "saat" in istek or "tarih" in istek:
        # AI Kararı: sistemi_dinle aracını çağır (Mac'te tarihi veren komut 'date'dir)
        sonuc = sistemi_dinle("date")
        
    else:
        sonuc = "Bu komut için bende bir 'Araç (Tool)' tanımlı değil."
        
    print(f"\n✅ AI AKSİYON RAPORU: {sonuc}")
    print("-" * 75)


# ================= 3. UYGULAMA (TESTLER) =================
if __name__ == "__main__":
    # Bota 3 farklı emir (Prompt) veriyoruz
    ai_ajani("Bana masaüstümde (burada) yeni bir klasör oluşturur musun?")
    ai_ajani("Şu an saat ve tarih tam olarak nedir?")
    ai_ajani("Bana içine mesaj bıraktığın bir dosya yaz!")

    print("\n👑 BÜYÜK FİNAL TAMAMLANDI! İşte sen benimle konuşurken, ben senin Mac bilgisayarına tam olarak bu OS kodlarıyla hükmediyordum.")
  