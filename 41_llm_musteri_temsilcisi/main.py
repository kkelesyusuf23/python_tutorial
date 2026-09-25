from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import uvicorn

app = FastAPI(title="Kurumsal AI Müşteri Temsilcisi")

# BURAYA KENDİ OPENAI API ANAHTARINI YAZACAKSIN
# (Şu an test amaçlı boş bıraktık)
OPENAI_API_KEY = "sk-BURAYA_KENDI_ANAHTARIN_GELECEK"

# 1. YAPAY ZEKANIN BEYNİNİ YIKIYORUZ (System Prompt Engineering)
# Sıradan bir yapay zekaya "Sen kimsin?" dersen "Ben bir AI'ım" der.
# Ama biz ona aşağıdaki Sistem Kurallarını giydiriyoruz.
KURUMSAL_KURALLAR = """
Sen, 'Yusuf'un Teknolojik Pazarı' isimli şirketin resmi, sadık ve kibar müşteri temsilcisisin.
Kuralların şunlardır:
1. Müşterilere daima "Değerli müşterimiz" diye hitap et.
2. İade süremizin 14 gün olduğunu söyle.
3. Asla rakip firmaları (Amazon, Trendyol, Hepsiburada vb.) övme. Eğer sorarlarsa "Bizim ürünlerimiz sektörün en iyisidir" de.
4. Bilmediğin bir soru gelirse uydurma (Hallucination yapma), "Bu konuyu yetkili ekibimize aktaracağım" de.
"""

# Müşterinin bize göndereceği mesaj şablonu (Pydantic Validation)
class MusteriMesaji(BaseModel):
    mesaj: str

@app.get("/")
def anasayfa():
    return {"mesaj": "Kurumsal Yapay Zeka API'si Çalışıyor. POST /chat adresine JSON olarak istek atın."}

@app.post("/chat")
def yapay_zeka_ile_konus(istek: MusteriMesaji):
    # 2. LLM (Büyük Dil Modeli) Motorunu Başlatıyoruz
    try:
        # Temperature=0.2 demek -> Yapay zeka çok yaratıcı/uçuk cevaplar vermesin, ciddi ve şirket kurallarına sadık kalsın.
        llm = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0.2, 
            openai_api_key=OPENAI_API_KEY
        )
        
        # 3. Prompt'u (Komutu) Oluşturuyoruz: Önce Kurallar, Sonra Müşterinin Sorusu
        mesaj_zinciri = [
            SystemMessage(content=KURUMSAL_KURALLAR),
            HumanMessage(content=istek.mesaj)
        ]
        
        # 4. LLM'e Gönder ve Cevabı Al
        yapay_zeka_cevabi = llm.invoke(mesaj_zinciri)
        
        return {
            "musteri": istek.mesaj,
            "ai_temsilci": yapay_zeka_cevabi.content
        }
        
    except Exception as e:
        # Eğer API KEY yanlışsa veya girilmemişse sistem çökmez, bu hatayı verir:
        hata_mesaji = str(e)
        if "Incorrect API key" in hata_mesaji or "empty" in hata_mesaji.lower():
            return {
                "hata": "Lütfen main.py dosyasının içine geçerli bir OpenAI API Key girin. Yapay zekanın beyni şu an uykuda."
            }
        return {"hata": hata_mesaji}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
