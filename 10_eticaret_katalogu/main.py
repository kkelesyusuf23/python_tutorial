from fastapi import FastAPI, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from veritabani import SessionLocal, Urun, test_verisi_ekle
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Veritabanı Session yönetimi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sunucu ilk ayağa kalktığında otomatik olarak test verilerini ekle (Varsa eklemez)
@app.on_event("startup")
def startup_event():
    test_verisi_ekle()

# ========================================================
# ANA SAYFA ROTASI (FİLTRELEME VE SAYFALAMANIN KALBİ)
# ========================================================
@app.get("/", response_class=HTMLResponse)
def katalog_goster(
    request: Request,
    # Arama kelimesi URL'den gelir (?arama=telefon). Optional demek, zorunlu değil demektir.
    arama: Optional[str] = Query(None),
    # Kategori URL'den gelir (?kategori=elektronik).
    kategori: Optional[str] = Query(None),
    # Sayfa numarası URL'den gelir (?sayfa=1). Varsayılanı 1'dir.
    sayfa: int = Query(1),
    db: Session = Depends(get_db)
):
    # 0. AYAR: Sayfa başına kaç ürün gösterileceğini belirliyoruz (Limitleme Sayısı)
    SAYFA_BASINA_URUN = 6
    
    # 1. TEMEL SORGUNUN OLUŞTURULMASI
    # Tüm ürünleri çekmek için temel sorguyu başlatıyoruz ama henüz veritabanını YORMUYORUZ (.all() yazmadık!)
    sorgu = db.query(Urun)
    
    # 2. ARAMA MANTIĞI (LIKE komutu)
    if arama:
        # .filter() veritabanında süzgeç görevi görür.
        # Urun.isim.contains(arama) -> Ürünün adının İÇİNDE bu harfler geçiyor mu diye kontrol eder.
        # Büyük/küçük harf duyarlılığı olmaması için genelde sunucuda veya veritabanında lower() kullanılabilir, biz basit tutuyoruz.
        sorgu = sorgu.filter(Urun.isim.contains(arama))
        
    # 3. KATEGORİ FİLTRESİ
    if kategori:
        # Sadece kategorisi seçilen kategoriye EŞİT olanları süz.
        sorgu = sorgu.filter(Urun.kategori == kategori)
        
    # 4. TOPLAM ÜRÜN SAYISINI BULMA (Sayfalama Butonları İçin)
    # Filtrelemeler bittikten sonra elimizde kaç ürün kaldıysa sayısını alıyoruz (.count)
    toplam_urun_sayisi = sorgu.count()
    
    # Toplam Sayfa Sayısını Hesaplama (Örn: 20 ürün varsa ve sayfada 6 ürün gösteriliyorsa = 4 sayfa çıkar)
    toplam_sayfa = (toplam_urun_sayisi // SAYFA_BASINA_URUN) + (1 if toplam_urun_sayisi % SAYFA_BASINA_URUN > 0 else 0)
    
    # 5. SAYFALAMA (PAGINATION) MANTIĞI: LIMIT ve OFFSET
    # OFFSET: Kaçıncı üründen itibaren atlayarak çekmeye başlayacağımızı söyler.
    # Örnek: 2. sayfadaysak -> (2 - 1) * 6 = 6. Veritabanına der ki "İlk 6 ürünü ATLA, 7'den itibaren getir."
    atlama_miktari = (sayfa - 1) * SAYFA_BASINA_URUN
    
    # Artık süzülmüş sorgumuza diyoruz ki: 
    # - .offset(atlama_miktari) -> Baştaki şu kadar veriyi es geç (atla)
    # - .limit(SAYFA_BASINA_URUN) -> Bana sadece 6 tane ürün ver (Fazlasını indirme, RAM dolmasın)
    # - .all() -> Tetiği çek, veritabanına bağlan ve sonucu bana liste olarak (Array) ver!
    urunler = sorgu.offset(atlama_miktari).limit(SAYFA_BASINA_URUN).all()
    
    # HTML dosyasına bu verileri gönderiyoruz ki ekranda çizebilelim
    return templates.TemplateResponse("index.html", {
        "request": request,
        "urunler": urunler,
        "arama": arama or "",
        "kategori": kategori or "",
        "suanki_sayfa": sayfa,
        "toplam_sayfa": toplam_sayfa
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
