import hashlib
import json

class Blok:
    def __init__(self, index, onceki_hash, oy_verisi):
        self.index = index
        self.onceki_hash = onceki_hash
        self.oy_verisi = oy_verisi  # Örn: {'secmen': 'Yusuf', 'parti': 'A Partisi'}
        # Blok yaratılır yaratılmaz içindeki veriler mühürlenir (Şifrelenir)
        self.hash = self.sifrele()

    def sifrele(self):
        # Bloğun içindeki tüm verileri tek bir metin haline getirip SHA-256 ile şifreliyoruz
        # En ufak bir virgül değişse bile Hash tamamen değişir!
        blok_metni = str(self.index) + self.onceki_hash + json.dumps(self.oy_verisi, sort_keys=True)
        return hashlib.sha256(blok_metni.encode()).hexdigest()

class OylamaBlockchain:
    def __init__(self):
        # Genesis Bloğu (Zincirin ilk halkası, önceki hash'i 0'dır)
        ilk_blok = Blok(0, "0", {"baslangic": "Secim Basladi"})
        self.zincir = [ilk_blok]

    def oy_kullan(self, oy_verisi):
        son_blok = self.zincir[-1]
        yeni_blok = Blok(len(self.zincir), son_blok.hash, oy_verisi)
        self.zincir.append(yeni_blok)
        print(f"✅ OY MÜHÜRLENDİ! {oy_verisi['secmen']} -> {oy_verisi['parti']} (Şifre: {yeni_blok.hash[:15]}...)")

    def zincir_gecerli_mi(self):
        # Zincirdeki tüm blokları baştan sona tararız
        for i in range(1, len(self.zincir)):
            mevcut_blok = self.zincir[i]
            onceki_blok = self.zincir[i-1]

            # 1. Bloğun kendi içindeki veri sonradan değiştirilmiş mi?
            if mevcut_blok.hash != mevcut_blok.sifrele():
                return False
            
            # 2. Önceki blokla bağlantısı (Kilit Sistemi) kopmuş mu?
            if mevcut_blok.onceki_hash != onceki_blok.hash:
                return False
                
        return True

if __name__ == "__main__":
    print("⛓️  KENDİ MİNİ-BLOCKCHAIN (OYLAMA) SİSTEMİMİZ BAŞLATILIYOR...\n")

    secim_sistemi = OylamaBlockchain()

    # 3 Kişi oy kullanıyor ve hepsi şifrelenip blokzincire ekleniyor
    secim_sistemi.oy_kullan({"secmen": "Ahmet", "parti": "A Partisi"})
    secim_sistemi.oy_kullan({"secmen": "Yusuf", "parti": "B Partisi"})
    secim_sistemi.oy_kullan({"secmen": "Ayse", "parti": "A Partisi"})

    print(f"\n🔒 Oylar güvende mi? (Hile Var Mı?): {secim_sistemi.zincir_gecerli_mi()}")
    print("-" * 65)

    # ================= HACKER SALDIRISI =================
    print("\n⚠️  DİKKAT: BİR HACKER İÇERİ SIZDI VE YUSUF'UN OYUNU DEĞİŞTİRDİ!")
    # Hacker, Yusuf'un B Partisine verdiği oyu veritabanında "A Partisi" olarak değiştiriyor
    secim_sistemi.zincir[2].oy_verisi = {"secmen": "Yusuf", "parti": "A Partisi"}

    print(f"🚨 Sistem Kontrol Ediliyor... (Hile Var Mı?): {secim_sistemi.zincir_gecerli_mi()}")

    if not secim_sistemi.zincir_gecerli_mi():
        print("❌ SİSTEM HİLEYİ ANINDA YAKALADI! ZİNCİR KOPTU VE OYLAMA İPTAL EDİLDİ.")
 