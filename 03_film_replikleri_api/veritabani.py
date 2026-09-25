from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


motor = create_engine("sqlite:///replikler.db", echo=False)
Ana_model = declarative_base()
class Replik(Ana_model):
    __tablename__ = "Replikler"
    id = Column(Integer, primary_key=True, autoincrement = True)
    film_adi = Column(String, nullable = False)
    karakter = Column(String, nullable = False)
    soz = Column(String, nullable= False)

Oturum = sessionmaker(bind=motor)

if __name__ == "__main__":
    Ana_model.metadata.create_all(motor)
    print("Veritabanı ve tablolar SQLAlchemy ile başarıyla oluşturuldu!")
