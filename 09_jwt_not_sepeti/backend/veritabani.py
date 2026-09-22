from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import bcrypt

# Veritabanı motoru (Backend klasöründe oluşturulacak)
engine = create_engine("sqlite:///jwt_notlar.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def sifre_hashle(sifre: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sifre.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def sifre_dogrula(duz_sifre: str, hashli_sifre: str):
    return bcrypt.checkpw(duz_sifre.encode('utf-8'), hashli_sifre.encode('utf-8'))

# 1. KULLANICI TABLOSU
class Kullanici(Base):
    __tablename__ = "kullanicilar"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_adi = Column(String, unique=True, index=True)
    # Şifreyi açıkça yazmayacağız, sadece karmaşık Hash halini tutacağız
    sifre_hash = Column(String)
    
    # Kullanıcının Notlarına erişim bağı
    notlar = relationship("Not", back_populates="sahibi")

# 2. NOT TABLOSU (Sadece yetkili kullanıcı kendi notlarını görebilir)
class Not(Base):
    __tablename__ = "notlar"
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String)
    icerik = Column(Text)
    
    # Bu not hangi kullanıcıya ait? (Foreign Key)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    sahibi = relationship("Kullanici", back_populates="notlar")

Base.metadata.create_all(bind=engine)
