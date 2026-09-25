import sys
import database
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

class FinansUygulamasi(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Kişisel Finans Takipçisi")
        self.resize(700, 500)
        self.setStyleSheet("background-color: #2b2b2b; color: white; font-size: 14px;")
        
        ana_duzen = QVBoxLayout()
        
        # 1. Başlık
        baslik = QLabel("Kişisel Finans Takipçisi")
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # --- YENİ: Özet (Bakiye) Ekranı ---
        ozet_duzeni = QHBoxLayout()
        
        self.gelir_etiketi = QLabel("Gelir: 0 ₺")
        self.gelir_etiketi.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")
        ozet_duzeni.addWidget(self.gelir_etiketi)
        
        self.gider_etiketi = QLabel("Gider: 0 ₺")
        self.gider_etiketi.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold;")
        ozet_duzeni.addWidget(self.gider_etiketi)
        
        self.bakiye_etiketi = QLabel("Bakiye: 0 ₺")
        self.bakiye_etiketi.setStyleSheet("color: #2196F3; font-size: 18px; font-weight: bold;")
        ozet_duzeni.addWidget(self.bakiye_etiketi)
        
        ana_duzen.addLayout(ozet_duzeni)
        
        # 2. Girdi Alanları
        form_duzeni = QHBoxLayout()
        
        self.tur_secici = QComboBox()
        self.tur_secici.addItems(["Gelir", "Gider"])
        self.tur_secici.setStyleSheet("background-color: #404040; padding: 5px;")
        form_duzeni.addWidget(self.tur_secici)
        
        self.miktar_kutusu = QLineEdit()
        self.miktar_kutusu.setPlaceholderText("Miktar (Örn: 150.50)")
        self.miktar_kutusu.setStyleSheet("background-color: #404040; padding: 5px;")
        form_duzeni.addWidget(self.miktar_kutusu)
        
        self.aciklama_kutusu = QLineEdit()
        self.aciklama_kutusu.setPlaceholderText("Açıklama (Örn: Market)")
        self.aciklama_kutusu.setStyleSheet("background-color: #404040; padding: 5px;")
        form_duzeni.addWidget(self.aciklama_kutusu)
        
        ana_duzen.addLayout(form_duzeni)
        
        # 3. Kaydet Butonu
        kaydet_butonu = QPushButton("İşlemi Kaydet")
        kaydet_butonu.setStyleSheet("background-color: #0078D7; font-weight: bold; padding: 10px; margin-top: 10px;")
        kaydet_butonu.clicked.connect(self.veriyi_kaydet)
        ana_duzen.addWidget(kaydet_butonu)
        
        # 4. YENİ EKLENEN KISIM: Geçmiş İşlemler Tablosu
        tablo_basligi = QLabel("Geçmiş İşlemler")
        tablo_basligi.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        ana_duzen.addWidget(tablo_basligi)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4) # 4 Sütun (Tür, Miktar, Açıklama, Tarih)
        self.tablo.setHorizontalHeaderLabels(["Tür", "Miktar (₺)", "Açıklama", "Tarih"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Sütunları ekrana yay
        self.tablo.setStyleSheet("background-color: #1e1e1e; gridline-color: #555555;")
        ana_duzen.addWidget(self.tablo)
        
        # 5. Sil Butonu (Kırmızı renkli)
        sil_butonu = QPushButton("Seçili İşlemi Sil")
        sil_butonu.setStyleSheet("background-color: #D32F2F; font-weight: bold; padding: 10px; margin-top: 10px;")
        sil_butonu.clicked.connect(self.veriyi_sil)
        ana_duzen.addWidget(sil_butonu)
        
        self.setLayout(ana_duzen)
        
        # Ekran açılır açılmaz verileri veritabanından çekip tabloya doldur
        self.tabloyu_guncelle()

    def veriyi_kaydet(self):
        tur = self.tur_secici.currentText()
        miktar = self.miktar_kutusu.text()
        aciklama = self.aciklama_kutusu.text()
        bugunun_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not miktar:
            QMessageBox.warning(self, "Hata", "Lütfen bir miktar girin!")
            return
            
        try:
            miktar_sayi = float(miktar)
            database.islem_ekle(tur, miktar_sayi, aciklama, bugunun_tarihi)
            
            # Başarılı kayıt sonrası kutuları temizle ve TABLOYU YENİLE
            self.miktar_kutusu.clear()
            self.aciklama_kutusu.clear()
            self.tabloyu_guncelle()
            
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir sayı girin!")

    # YENİ EKLENEN KISIM: Veritabanından verileri çekip arayüze çizme
    def tabloyu_guncelle(self):
        # 1. database.py dosyamızdaki okuma fonksiyonunu çağırıyoruz
        veriler = database.tum_islemleri_getir()
        
        # 2. Tablodaki satır sayısını veritabanından gelen satır sayısı kadar yap
        self.tablo.setRowCount(len(veriler))
        
        # 3. Tüm verileri döngüyle dönüp tablo hücrelerine (Item) yerleştir
        for satir_indeksi, islem in enumerate(veriler):
            # islem = [id, tur, miktar, aciklama, tarih]
            tur_hucresi = QTableWidgetItem(islem["tur"])
            tur_hucresi.setData(Qt.UserRole, islem["id"]) # ID'yi gizlice hücreye göm
            self.tablo.setItem(satir_indeksi, 0, tur_hucresi)
            
            self.tablo.setItem(satir_indeksi, 1, QTableWidgetItem(str(islem["miktar"])))
            self.tablo.setItem(satir_indeksi, 2, QTableWidgetItem(islem["aciklama"]))
            self.tablo.setItem(satir_indeksi, 3, QTableWidgetItem(islem["tarih"]))
            
        # 4. YENİ: Bakiye etiketlerini güncelle
        ozet = database.bakiye_hesapla()
        self.gelir_etiketi.setText(f"Gelir: {ozet['gelir']} ₺")
        self.gider_etiketi.setText(f"Gider: {ozet['gider']} ₺")
        self.bakiye_etiketi.setText(f"Bakiye: {ozet['bakiye']} ₺")

    def veriyi_sil(self):
        # Seçili olan satırı bul
        secili_satir = self.tablo.currentRow()
        
        # Eğer hiçbir satır seçilmediyse uyarı ver
        if secili_satir == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silmek için tablodan bir satır seçin!")
            return
            
        # Kullanıcıdan silmek istediğine emin mi diye onay iste
        cevap = QMessageBox.question(self, "Onay", "Bu işlemi silmek istediğinize emin misiniz?", 
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        if cevap == QMessageBox.Yes:
            # Seçili satırın 0. sütunundaki (gizlice gömdüğümüz) ID'yi al
            secili_id = self.tablo.item(secili_satir, 0).data(Qt.UserRole)
            
            # Veritabanından sil
            database.islem_sil(secili_id)
            
            # Tabloyu yenile ki ekrandan da kaybolsun
            self.tabloyu_guncelle()
            QMessageBox.information(self, "Başarılı", "İşlem silindi!")

# Uygulamayı Başlat
if __name__ == "__main__":
    uygulama = QApplication(sys.argv)
    pencere = FinansUygulamasi()
    pencere.show()
    sys.exit(uygulama.exec_())
