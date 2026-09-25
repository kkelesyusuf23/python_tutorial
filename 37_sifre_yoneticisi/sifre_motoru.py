import base64
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VERITABANI = "sifreler.json"
# Çok gizli bir tuz (Salt). Gerçek dünyada bu da rastgele üretilip saklanır.
TUZ = b"yusuf_keles_super_gizli_tuz" 

def anahtar_uret(ana_sifre: str) -> bytes:
    """
    Kullanıcının girdiği 'Ana Şifre'den (Örn: yusuf123)
    askeri standartlarda (AES) bir kriptografik anahtar üretir.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=TUZ,
        iterations=100000,
    )
    anahtar = base64.urlsafe_b64encode(kdf.derive(ana_sifre.encode()))
    return anahtar

def sifre_kaydet(ana_sifre: str, platform: str, sifre: str):
    """
    Kullanıcının platform şifresini şifreleyip (Encrypt) JSON'a yazar.
    """
    anahtar = anahtar_uret(ana_sifre)
    f = Fernet(anahtar)
    
    # 1. Şifrelenecek metni bytes'a çevir ve şifrele
    sifreli_metin = f.encrypt(sifre.encode()).decode()
    
    # 2. Mevcut veritabanını oku (Eğer varsa)
    veriler = {}
    if os.path.exists(VERITABANI):
        with open(VERITABANI, "r") as dosya:
            veriler = json.load(dosya)
            
    # 3. Yeni veriyi ekle ve kaydet (JSON dosyasında sadece şifreli metin durur)
    veriler[platform] = sifreli_metin
    with open(VERITABANI, "w") as dosya:
        json.dump(veriler, dosya, indent=4)

def sifreleri_getir(ana_sifre: str) -> dict:
    """
    JSON'dan şifreli verileri okuyup doğru anahtarla çözer (Decrypt).
    Eğer Ana Şifre yanlışsa hata fırlatır!
    """
    if not os.path.exists(VERITABANI):
        return {}
        
    anahtar = anahtar_uret(ana_sifre)
    f = Fernet(anahtar)
    
    cozulmus_veriler = {}
    with open(VERITABANI, "r") as dosya:
        veriler = json.load(dosya)
        
    for platform, sifreli_metin in veriler.items():
        try:
            # Şifreli metni çöz ve sözlüğe ekle
            cozulmus_metin = f.decrypt(sifreli_metin.encode()).decode()
            cozulmus_veriler[platform] = cozulmus_metin
        except Exception:
            # Eğer Ana Şifre yanlışsa decrypt işlemi çöker.
            raise ValueError("Ana Şifre Yanlış!")
            
    return cozulmus_veriler
