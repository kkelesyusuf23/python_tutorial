from web3 import Web3

print("🌐 Web3.py Motoru Çalıştırılıyor...\n")
print("⛓️ Ethereum Blockchain Ağına Bağlanılıyor (Cloudflare Node Üzerinden)...")

# 1. NODE BAĞLANTISI (Blockchain'e Giriş Kapısı)
# Web3 uygulamaları veritabanı (MySQL/PostgreSQL) kullanmaz. Onun yerine Node (Düğüm) kullanır.
node_url = "https://ethereum-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(node_url))

# Bağlantı testi
if w3.is_connected():
    print("✅ BAĞLANTI BAŞARILI! Şu an milyonlarca dolarlık Ethereum Ağının İçindeyiz.\n")
else:
    print("❌ Bağlantı Başarısız! Lütfen internetinizi kontrol edin.")
    exit()

# 2. CÜZDAN SORGULAMA (Şeffaflık İlkesi)
# Blockchain'in en büyük özelliği, dünyadaki herkesin cüzdanını görebilmenizdir (Anonim ama Şeffaf).
# Hedef: Ethereum'u kuran vakfın (Ethereum Foundation) ana cüzdanı
hedef_cuzdan = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"

print(f"💼 Hedef Cüzdan Adresi: {hedef_cuzdan}")
print("🔄 Bakiye Blockchain'in devasa defterinden (Ledger) canlı olarak sorgulanıyor...\n")

# Bakiye, Ethereum'un en küçük birimi olan "Wei" cinsinden gelir (1 ETH = 10^18 Wei)
bakiye_wei = w3.eth.get_balance(hedef_cuzdan)

# Okuyabilmek için Wei'yi Ether'e (ETH) dönüştürüyoruz
bakiye_eth = w3.from_wei(bakiye_wei, 'ether')

print("--- 💰 CANLI CÜZDAN BİLGİLERİ ---")
print(f"Toplam Bakiye: {bakiye_eth} ETH")
print("---------------------------------\n")

print("🚀 TEBRİKLER! Borsa (Binance) veya banka olmadan, kendi kodlarınla Matrix'e (Blockchain'e) doğrudan sızmayı başardın.")
