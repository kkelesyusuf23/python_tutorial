from transformers import pipeline
from PIL import Image
import requests
import io

print("🧠 HuggingFace'ten Google ViT (Görme) Modeli İndiriliyor/Yükleniyor...")
print("⚠️ (Eğer kodu ilk defa çalıştırıyorsan modelin inmesi internet hızına göre 1-2 dakika sürebilir, bekle...)")

# HuggingFace kütüphanesi sayesinde sadece 1 satır kodla Google'ın devasa modelini çekiyoruz
gorsel_taniyici = pipeline("image-classification", model="google/vit-base-patch16-224")

def resmi_tani(resim_url: str):
    """ Verilen URL'deki resmi alıp Yapay Zekaya (Model'e) tahmin ettirir. """
    print(f"\n🔍 Resim Analiz Ediliyor: {resim_url}")
    
    # 1. Resmi internetten çekip RAM'e (BytesIO) alıyoruz (Wikipedia botları engellemesin diye User-Agent ekliyoruz)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    cevap = requests.get(resim_url, headers=headers)
    resim = Image.open(io.BytesIO(cevap.content))
    
    # 2. HUGGINGFACE SİHRİ: Resmi modele ver ve tahminleri al
    sonuclar = gorsel_taniyici(resim)
    
    # 3. Sonuçları ekrana şık bir şekilde yazdır
    print("--- 🤖 YAPAY ZEKA TAHMİNLERİ ---")
    for sonuc in sonuclar:
        # Sonuç örneği: {'label': 'Egyptian cat', 'score': 0.8523}
        oran = round(sonuc['score'] * 100, 2)
        isim = sonuc['label'].upper()
        print(f"👉 %{oran} ihtimalle bu bir: {isim}")
    print("---------------------------------\n")

if __name__ == "__main__":
    # Test 1: HuggingFace'in kendi resmi Kedi fotoğrafı (Botları engellemez)
    kedi_resmi = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/pipeline-cat-chonk.jpeg"
    resmi_tani(kedi_resmi)
    
    # Test 2: PyTorch'un resmi Köpek (Golden Retriever) fotoğrafı
    kopek_resmi = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
    resmi_tani(kopek_resmi)
    
    print("✅ Test Tamamlandı. İstersen koda girip kendi resim URL'ni ekleyebilirsin!")
 