from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

motor = create_engine("sqlite:///urlkisaltici.db", echo=False)
Ana_model = declarative_base()

class Link(Ana_model):
    __tablename__ = "Linkler"
    id = Column(Integer, primary_key=True)
    uzun_url = Column(String, nullable=False)
    kisa_kod = Column(String, unique=True, nullable=False)
    tiklanma_sayisi = Column(Integer, default=0)

Oturum = sessionmaker(bind=motor)

if __name__ == "__main__":
    Ana_model.metadata.create_all(motor)
    print("Veritabanı ve Link tablosu başarıyla oluşturuldu!")
