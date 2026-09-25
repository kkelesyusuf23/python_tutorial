import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
import uvicorn

# ==========================================
# 1. VERİ MODELİ (STRAWBERRY TİPLERİ)
# ==========================================
# Pydantic (BaseModel) yerine GraphQL nesneleri kullanıyoruz.
@strawberry.type
class Urun:
    id: int
    ad: str
    fiyat: float
    stokta_var_mi: bool

# Sahte Veritabanımız
urun_veritabani = [
    Urun(id=1, ad="MacBook Pro M3", fiyat=1999.99, stokta_var_mi=True),
    Urun(id=2, ad="iPhone 15 Pro", fiyat=999.99, stokta_var_mi=False),
    Urun(id=3, ad="AirPods Pro", fiyat=249.99, stokta_var_mi=True),
]


# ==========================================
# 2. QUERY (SORGULAR - VERİ ÇEKME)
# ==========================================
# Geleneksel REST API'deki GET İsteklerinin karşılığıdır.
@strawberry.type
class Query:
    
    @strawberry.field
    def tum_urunler(self) -> List[Urun]:
        return urun_veritabani

    @strawberry.field
    def urun_getir(self, urun_id: int) -> Optional[Urun]:
        for u in urun_veritabani:
            if u.id == urun_id:
                return u
        return None


# ==========================================
# 3. MUTATION (DEĞİŞİMLER - VERİ YAZMA)
# ==========================================
# Geleneksel REST API'deki POST/PUT/DELETE İsteklerinin karşılığıdır.
@strawberry.type
class Mutation:
    
    @strawberry.mutation
    def urun_ekle(self, ad: str, fiyat: float, stokta_var_mi: bool) -> Urun:
        yeni_id = len(urun_veritabani) + 1
        yeni_urun = Urun(id=yeni_id, ad=ad, fiyat=fiyat, stokta_var_mi=stokta_var_mi)
        urun_veritabani.append(yeni_urun)
        return yeni_urun


# ==========================================
# 4. FASTAPI ENTEGRASYONU
# ==========================================
# Yukarıdaki Query ve Mutation sınıflarını birleştirip bir GraphQL Şeması (Kurallar Bütünü) yaratıyoruz.
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()

# Geleneksel REST API'lerdeki gibi 100 farklı rota yazmıyoruz. 
# Tüm GraphQL sistemi SADECE "/graphql" kapısından çalışır!
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
