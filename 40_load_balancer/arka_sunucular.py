from fastapi import FastAPI
import uvicorn
import sys

app = FastAPI()

# Terminalden gelen port numarasını al (Örn: 8001)
# Eğer port verilmezse 8001 kullan
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

@app.get("/")
def islem_yap():
    """ 
    Trendyol/Netflix sunucusu gibi düşünebilirsin. 
    İşlemi hangi kopyanın yaptığını müşteriye dönüyoruz ki Load Balancer'ın çalıştığını görelim.
    """
    return {
        "mesaj": "İşleminiz başarıyla gerçekleştirildi!",
        "isleme_alan_sunucu": f"Sunucu (Port {PORT})"
    }

if __name__ == "__main__":
    print(f"[{PORT}] Numaralı Kopya Sunucu Başlatılıyor...")
    uvicorn.run("arka_sunucular:app", host="127.0.0.1", port=PORT)
