from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import uvicorn

app = FastAPI(title="Haber Botu API")

@app.get("/")
def anasayfa():
    return {"mesaj": "Kendi API'mize Hoşgeldiniz. Güncel haberleri çekmek için /haberler rotasına gidin."}

@app.get("/haberler")
def haberleri_getir():
    """ 
    Dış dünyadaki bir siteye sanal bir bot yollayıp 
    verilerini kazıdığımız (Scraping) API Rotası 
    """
    
    # 1. Hedef siteye görünmez bir bot olarak istek atıyoruz
    url = "https://news.ycombinator.com/"
    
    # Bazı siteler "sen botsun" deyip engeller. Bu yüzden "Ben Mac kullanıcısı, normal bir Chrome tarayıcısıyım" taklidi (User-Agent) yapıyoruz.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    cevap = requests.get(url, headers=headers)
      
    # Eğer site çökmüşse veya bizi engellemişse hata dön
    if cevap.status_code != 200:
        return {"hata": "Hedef siteye ulaşılamadı", "durum_kodu": cevap.status_code}
        
    # 2. Gelen milyonlarca satır karmaşık HTML yığınını BeautifulSoup'un bıçağıyla parçalıyoruz (Parsing)
    soup = BeautifulSoup(cevap.text, "html.parser")
    
    haberler = []
    
    # 3. KAZIMA İŞLEMİ (Scraping)
    # HackerNews sitesinde (HTML kaynak kodunda) haber başlıkları "titleline" sınıfına (class) sahip span'lerin içinde a etiketlerindedir.
    # Sayfadaki ilk 10 haberi bulup ayıklıyoruz
    basliklar = soup.find_all("span", class_="titleline", limit=10)
    
    for idx, baslik_kutusu in enumerate(basliklar):
        # İçindeki ilk linki (a etiketi) bul
        link_etiketi = baslik_kutusu.find("a")
        if link_etiketi:
            haber_basligi = link_etiketi.text
            haber_linki = link_etiketi.get("href")
            
            haberler.append({
                "id": idx + 1,
                "baslik": haber_basligi,
                "kaynak_url": haber_linki
            })
            
    # 4. Ayıkladığımız verileri kendi API'miz üzerinden pırıl pırıl JSON formatında müşterilerimize (mobil uygulamalara) servis ediyoruz!
    return {
        "api_sahibi": "Yusuf'un Botu",
        "toplam_haber": len(haberler),
        "haberler": haberler
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
