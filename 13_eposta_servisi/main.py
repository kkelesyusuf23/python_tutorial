from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ========================================================
# ADIM 4: ARKA PLAN (BACKGROUND) GÖREV FONKSİYONU
# ========================================================
# Bu fonksiyon normal bir rota (endpoint) değildir. 
# Gelen e-posta listesini parçalayarak her birine mail atıyormuş gibi yapar (Simülasyon).
async def mail_gonder_simulasyonu(alicilar: str, mesaj: str):
    # 'ahmet@a.com, mehmet@b.com' şeklindeki yazıyı virgüllerden ayırıp listeye çeviriyoruz.
    mail_listesi = [mail.strip() for mail in alicilar.split(",")]
    
    # Her bir kullanıcı için teker teker işlem yap
    for i, eposta in enumerate(mail_listesi, 1):
        # Eğer bu gerçek bir mail olsaydı 'smtplib' kullanarak Google'a bağlanacaktık.
        # Simülasyon olduğu için 2 saniye bekletiyoruz (Mail göndermek ağırdır).
        await asyncio.sleep(2)
        print(f"[ARKA PLAN] {i}/{len(mail_listesi)} -> {eposta} adresine mail başarıyla gönderildi!")
        print(f"Mesaj: {mesaj}\n{'-'*30}")
        
    print("[ARKA PLAN BAŞARILI] Tüm maillerin gönderimi tamamlandı!")

# ========================================================
# ADIM 3: ANA SAYFA ROTASI
# ========================================================
@app.get("/", response_class=HTMLResponse)
def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ========================================================
# ADIM 5: GÖNDER ROTASI (BACKGROUND TASKS TETİKLEYİCİSİ)
# ========================================================
@app.post("/gonder")
def mail_baslat(
    background_tasks: BackgroundTasks, # FastAPI'den özel arka plan görev yöneticisini alıyoruz
    alicilar: str = Form(...),
    mesaj: str = Form(...)
):
    # KRİTİK NOKTA: 
    # Fonksiyonu (mail_gonder_simulasyonu) doğrudan ÇAĞIRMIYORUZ! (Yani yanına () koymuyoruz)
    # Bunun yerine FastAPI'nin arka plan yöneticisine ekliyoruz.
    background_tasks.add_task(mail_gonder_simulasyonu, alicilar, mesaj)
    
    # Biz arka plan görevini yöneticisine verdik. FastAPI bunu arka planda çalıştırırken, 
    # biz KULLANICIYI HİÇ BEKLETMEDEN saniyesinde cevap dönüyoruz!
    return {
        "durum": "Başarılı", 
        "mesaj": f"{len(alicilar.split(','))} kişiye mail gönderim işlemi arka planda başlatıldı! Lütfen terminal loglarını izleyin."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
