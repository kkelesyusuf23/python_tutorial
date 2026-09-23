from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Veritabanı motorunu kuruyoruz (SQLite dosyası)
engine = create_engine("sqlite:///katalog.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Ürün Tablosu Modeli
class Urun(Base):
    __tablename__ = "urunler"
    
    # Her ürünün benzersiz kimliği (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    # Ürünün adı (Arama yapacağımız yer)
    isim = Column(String, index=True)
    # Ürünün kategorisi (Filtreleme yapacağımız yer)
    kategori = Column(String, index=True)
    # Ürünün fiyatı
    fiyat = Column(Float)

# Tabloları fiziksel olarak oluştur
Base.metadata.create_all(bind=engine)

# ========================================================
# EĞİTİM İÇİN ÖZEL FONKSİYON: Rastgele Veri Ekleme (Seeding)
# ========================================================
# Eğer veritabanı boşsa, test yapabilmemiz için içeriye otomatik 25 tane ürün atar.
def test_verisi_ekle():
    db = SessionLocal()
    # Eğer tabloda hiç ürün yoksa (Sıfırsa)
    if db.query(Urun).count() == 0:
        ornek_urunler = [
            # Elektronik
            Urun(isim="iPhone 15 Pro", kategori="Elektronik", fiyat=65000),
            Urun(isim="MacBook Air M2", kategori="Elektronik", fiyat=45000),
            Urun(isim="AirPods Pro", kategori="Elektronik", fiyat=8000),
            Urun(isim="Samsung Galaxy S24", kategori="Elektronik", fiyat=55000),
            Urun(isim="Sony WH-1000XM5 Kulaklık", kategori="Elektronik", fiyat=12000),
            Urun(isim="LG 55 inç 4K TV", kategori="Elektronik", fiyat=25000),
            Urun(isim="Dyson V15 Süpürge", kategori="Elektronik", fiyat=22000),
            # Giyim
            Urun(isim="Nike Air Max Ayakkabı", kategori="Giyim", fiyat=4500),
            Urun(isim="Levi's 501 Kot Pantolon", kategori="Giyim", fiyat=2000),
            Urun(isim="Zara Kışlık Mont", kategori="Giyim", fiyat=3500),
            Urun(isim="Adidas Spor Tişört", kategori="Giyim", fiyat=800),
            Urun(isim="Mavi Keten Gömlek", kategori="Giyim", fiyat=1200),
            Urun(isim="Puma Antrenman Eşofmanı", kategori="Giyim", fiyat=1800),
            # Kitap
            Urun(isim="Simyacı - Paulo Coelho", kategori="Kitap", fiyat=150),
            Urun(isim="1984 - George Orwell", kategori="Kitap", fiyat=120),
            Urun(isim="Suç ve Ceza - Dostoyevski", kategori="Kitap", fiyat=180),
            Urun(isim="Yüzüklerin Efendisi Serisi", kategori="Kitap", fiyat=500),
            Urun(isim="Harry Potter Felsefe Taşı", kategori="Kitap", fiyat=200),
            Urun(isim="Sefiller - Victor Hugo", kategori="Kitap", fiyat=220),
            # Ev Yaşam
            Urun(isim="Karaca Fincan Takımı", kategori="Ev Yaşam", fiyat=900),
            Urun(isim="Tefal Düdüklü Tencere", kategori="Ev Yaşam", fiyat=3500),
            Urun(isim="IKEA Çalışma Masası", kategori="Ev Yaşam", fiyat=4000),
            Urun(isim="Philips Fritöz (Airfryer)", kategori="Ev Yaşam", fiyat=6000),
            Urun(isim="Paşabahçe Bardak Seti", kategori="Ev Yaşam", fiyat=400),
            Urun(isim="Taç Yatak Örtüsü", kategori="Ev Yaşam", fiyat=1500)
        ]
        # Bütün listeyi aynı anda veritabanına kaydet
        db.add_all(ornek_urunler)
        db.commit()
    db.close()
