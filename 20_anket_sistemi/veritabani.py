from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# SQLite veritabanı bağlantısı
engine = create_engine("sqlite:///anketler.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Anket(Base):
    __tablename__ = "anketler"
    
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String, index=True)
    
    # SİHİRLİ KISIM: Soru sayısı ve seçenekler değişken olduğu için 
    # bunları tek bir sabit sütuna değil, esnek bir JSON sütununa hapsediyoruz.
    # Örnek İçerik: [{"soru": "Hangi renk?", "secenekler": ["Kırmızı", "Mavi"]}, ...]
    sorular = Column(JSON) 
    
    # Bir anketin birden fazla oyu (katılımı) olabilir
    oylar = relationship("Oy", back_populates="anket", cascade="all, delete-orphan")

class Oy(Base):
    __tablename__ = "oylar"
    
    id = Column(Integer, primary_key=True, index=True)
    anket_id = Column(Integer, ForeignKey("anketler.id"))
    
    # Hangi soruya (index) hangi cevabın verildiğini JSON olarak tutuyoruz.
    # Örnek İçerik: {"0": "Kırmızı", "1": "Evet"}
    cevaplar = Column(JSON)
    
    anket = relationship("Anket", back_populates="oylar")

# Tabloları fiziksel olarak oluştur
Base.metadata.create_all(bind=engine)
