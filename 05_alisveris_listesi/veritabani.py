from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

motor = create_engine("sqlite:///alisverislistesi.db", echo=False)
Ana_model = declarative_base()

class Urun(Ana_model):
    __tablename__ = "Alisverisler"
    id = Column(Integer, primary_key=True)
    urun_adi = Column(String)
    alindi_mi = Column(Boolean, default=False)
    miktar = Column(Integer, default=1)

Oturum = sessionmaker(bind=motor)

if __name__ == "__main__":
    Ana_model.metadata.create_all(motor)
    print("Veritabanı oluşturuldu!")
