import ast

print("🕵️‍♂️ Senior Yazılımcı (Linter) Botu Başlatılıyor...\n")
print("📂 'hatali_kod.py' dosyası satır satır inceleniyor...\n")

# İnceleyeceğimiz dosyayı okuyoruz
with open("hatali_kod.py", "r") as dosya:
    kod_metni = dosya.read()

# 1. KODU AĞACA ÇEVİR (AST PARSE)
# Kodları sıradan bir metin (String) olmaktan çıkarıp, 
# Bilgisayarın anlayabileceği "Sözdizimi Ağacına (AST)" dönüştürüyoruz.
kod_agaci = ast.parse(kod_metni)

hatalar = []

# 2. AĞACIN DALLARINDA GEZİN (AST WALK)
for dugum in ast.walk(kod_agaci):
    
    # KURAL 1: 'import *' kullanmak YASAKTIR! (Tüm kütüphaneyi çekmek hafızayı yorar)
    # Eğer bu satır bir "ImportFrom" ise:
    if isinstance(dugum, ast.ImportFrom):
        for isim in dugum.names:
            if isim.name == '*':
                hatalar.append(f"SATIR {dugum.lineno}: 'import *' kullanılamaz! Hafızayı yormamak için sadece ihtiyacın olan fonksiyonu dahil et.")
                
    # KURAL 2: Her fonksiyonun bir Profesyonel Açıklaması (Docstring) olmak zorundadır.
    # Eğer bu satır bir "Fonksiyon Tanımı" ise:
    if isinstance(dugum, ast.FunctionDef):
        # ast kütüphanesi fonksiyonun açıklamasını otomatik kontrol eder
        if not ast.get_docstring(dugum):
            hatalar.append(f"SATIR {dugum.lineno}: '{dugum.name}' fonksiyonunda açıklama (Docstring) eksik!")

# 3. KOD İNCELEME (REVIEW) RAPORU
print("--- 📋 KOD İNCELEME RAPORU ---")
if hatalar:
    print("❌ KOD (COMMIT) REDDEDİLDİ! Aşağıdaki şirket kurallarına uymalısın:\n")
    for hata in hatalar:
        print(f"👉 {hata}")
else:
    print("✅ KOD ONAYLANDI! Yazılımın standartlara uygun.")

print("\n🚀 İşlem Tamam! Pylint, Flake8 gibi devasa yazılımların çekirdeğini (AST) inşa ettin.")
