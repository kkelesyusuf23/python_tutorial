from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# SQLite veritabanı dosyası (otel.db) projemizin içinde oluşacak
DATABASE_URL = "sqlite:///./otel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 1. KULLANICI TABLOSU
# ==========================================
class Kullanici(Base):
    __tablename__ = "kullanicilar"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_soyad = Column(String, nullable=False)
    eposta = Column(String, unique=True, nullable=False)
    
    # İLİŞKİ (Relationship): Bir kullanıcının birden fazla rezervasyonu olabilir.
    # SQL sorgusu yaparken (JOIN) işimizi kolaylaştıracak sihirli SQLAlchemy köprüsü.
    rezervasyonlar = relationship("Rezervasyon", back_populates="kullanici")


# ==========================================
# 2. ODA TABLOSU
# ==========================================
class Oda(Base):
    __tablename__ = "odalar"
    
    id = Column(Integer, primary_key=True, index=True)
    oda_numarasi = Column(String, unique=True, nullable=False)
    fiyat = Column(Float, nullable=False)
    
    # İLİŞKİ (Relationship): Bir oda geçmişte veya gelecekte birden fazla kez rezerve edilebilir.
    rezervasyonlar = relationship("Rezervasyon", back_populates="oda")


# ==========================================
# 3. REZERVASYON TABLOSU (KÖPRÜ TABLOSU)
# ==========================================
class Rezervasyon(Base):
    __tablename__ = "rezervasyonlar"
    
    id = Column(Integer, primary_key=True, index=True)
    giris_tarihi = Column(String, nullable=False)
    cikis_tarihi = Column(String, nullable=False)
    
    # ================= FOREIGN KEY =================
    # Yabancı Anahtar: Veritabanına şunu diyoruz: 
    # "Buradaki ID'ler rastgele rakamlar değildir, 
    # kullanicilar ve odalar tablolarındaki gerçek ID'leri işaret eder."
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    oda_id = Column(Integer, ForeignKey("odalar.id"))
    
    # SQLAlchemy'nin bu tabloları birleştirebilmesi (JOIN) için ters köprüler
    kullanici = relationship("Kullanici", back_populates="rezervasyonlar")
    oda = relationship("Oda", back_populates="rezervasyonlar")


# Her bir API isteğinde (FastAPI) veritabanına bağlanıp işlem bitince bağlantıyı kapatan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
