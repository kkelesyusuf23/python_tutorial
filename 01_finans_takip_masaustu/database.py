import sqlite3

def baglanti_al():
    baglanti = sqlite3.connect("finans.db")
    baglanti.row_factory = sqlite3.Row 
    return baglanti

def tablolari_olustur():
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tur TEXT NOT NULL,
            miktar REAL NOT NULL,
            aciklama TEXT,
            tarih TEXT NOT NULL
        )
    """)
    baglanti.commit()
    baglanti.close()

def islem_ekle(tur, miktar, aciklama, tarih):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    
    imlec.execute(
        "INSERT INTO islemler (tur, miktar, aciklama, tarih) VALUES (?, ?, ?, ?)",
        (tur, miktar, aciklama, tarih)
    )
    baglanti.commit()
    baglanti.close()

def tum_islemleri_getir():
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    
    imlec.execute("SELECT * FROM islemler ORDER BY tarih DESC")
    veriler = imlec.fetchall()
    baglanti.close()
    return veriler

def islem_sil(id):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    imlec.execute("DELETE FROM islemler WHERE id = ?", (id,))
    baglanti.commit()
    baglanti.close()

def bakiye_hesapla():
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    
    imlec.execute("SELECT SUM(miktar) FROM islemler WHERE tur = 'Gelir'")
    gelir = imlec.fetchone()[0] or 0.0
    
    imlec.execute("SELECT SUM(miktar) FROM islemler WHERE tur = 'Gider'")
    gider = imlec.fetchone()[0] or 0.0
    
    baglanti.close()
    return {"gelir": gelir, "gider": gider, "bakiye": gelir - gider}

# 7. İşlem Güncelleme
def islem_guncelle(id, tur, miktar, aciklama):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    
    imlec.execute(
        "UPDATE islemler SET tur=?, miktar=?, aciklama=? WHERE id=?",
        (tur, miktar, aciklama, id)
    )
    baglanti.commit()
    baglanti.close()

if __name__ == "__main__":
    tablolari_olustur()
    print("Veritabanı başarıyla kuruldu!")
