import stripe
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. STRIPE API ANAHTARI
# ==========================================
# DİKKAT: Stripe Dashboard'dan aldığın Test Gizli Anahtarını (Secret Key) buraya yapıştır.
# "sk_test_..." ile başlar. Şimdilik geçersiz bir anahtar koyuyoruz, testi başlatınca hata verecektir.
stripe.api_key = "sk_test_51SuLbeEOgeFBfZFSe6HiU0EMnJhWtFYPyGv1SVKZWBatMoBy20TYOir9arifxNW4F5BHaKAsrlwcLXx76KwOuWWz00n5grvTrW"


# ==========================================
# 2. ROTALAR VE ÖDEME ALTYAPISI
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/odeme-baslat")
async def odeme_baslat(request: Request):
    """
    Kullanıcı "Premium Satın Al" butonuna bastığında bu rota çalışır.
    Burada kendi sistemimizde ödeme almayız, Stripe sunucularından bizim için 
    güvenli bir ödeme sayfası (Checkout Session) yaratmasını isteriz.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'], # Sadece Kredi Kartı kabul et
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Pro Abonelik (Aylık)',
                            'description': 'Tüm premium özelliklere, reklamları kaldırmaya ve 7/24 desteğe erişim.',
                        },
                        # DİKKAT: Stripe kuruş (cent) üzerinden çalışır! 19.00 USD için 1900 yolluyoruz.
                        'unit_amount': 1900, 
                    },
                    'quantity': 1,
                },
            ],
            mode='payment', 
            success_url='http://127.0.0.1:8000/basarili', # Ödeme çekilirse buraya fırlat
            cancel_url='http://127.0.0.1:8000/',          # Adam vazgeçerse ana sayfaya fırlat
        )
        
        # Stripe'ın bizim için yarattığı Güvenli Ödeme linkine (URL) kullanıcıyı yönlendir.
        return RedirectResponse(checkout_session.url, status_code=303)
        
    except Exception as e:
        # Eğer API anahtarı yanlışsa buraya düşeriz
        return HTMLResponse(content=f"""
        <h3 style='color:red'>Stripe Hatası:</h3>
        <p>{str(e)}</p>
        <p><b>Muhtemelen geçerli bir Stripe API Anahtarı (sk_test_...) girmedin.</b> Lütfen main.py dosyasındaki api_key değişkenini güncelle.</p>
        """)


@app.get("/basarili")
async def basarili_odeme(request: Request):
    # Stripe, karttan parayı çektiğinde kullanıcıyı buraya yollar.
    # Gerçek projelerde burada Veritabanına gidip adamın rütbesini 'PREMIUM' yaparız.
    return templates.TemplateResponse("success.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
