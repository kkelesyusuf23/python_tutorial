from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Veritabanı motorunu oluşturuyoruz
engine = create_engine("sqlite:///kutuphane.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. YAZAR TABLOSU
class Yazar(Base):
    __tablename__ = "yazarlar"
    
    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String, index=True)
    ulke = Column(String)
    
    # İLİŞKİ: Bir yazarın birden çok kitabı olabilir (One-to-Many).
    # Kitap tablosundaki "yazar" ilişkisine referans verir.
    kitaplar = relationship("Kitap", back_populates="yazar")

# 2. KİTAP TABLOSU
class Kitap(Base):
    __tablename__ = "kitaplar"
    
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String, index=True)
    sayfa_sayisi = Column(Integer)
    
    # YABANCI ANAHTAR (Foreign Key): Bu kitabın yazarının ID'si nedir?
    yazar_id = Column(Integer, ForeignKey("yazarlar.id"))
    
    # İLİŞKİ: Bu kitap hangi yazara ait?
    yazar = relationship("Yazar", back_populates="kitaplar")

# Tabloları fiziksel olarak oluştur (Eğer yoksa sqlite dosyasını yaratır)
Base.metadata.create_all(bind=engine)
