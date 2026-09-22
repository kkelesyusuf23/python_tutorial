from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

motor = create_engine("sqlite:///itiraflar.db", echo=False)
Ana_model = declarative_base()

class Itiraf(Ana_model):
    __tablename__ = "Itiraflar"
    id = Column(Integer, primary_key=True)
    mesaj = Column(String)
    ip_adresi = Column(String)
    tarih = Column(String)


Oturum = sessionmaker(bind=motor)

if __name__ == "__main__":
    Ana_model.metadata.create_all(motor)
    print("veritabanı ve tablolar, sqlalcemy ile oluşturuldu")
