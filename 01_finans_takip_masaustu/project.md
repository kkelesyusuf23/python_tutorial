# Proje 1: Kişisel Finans Takipçisi (Masaüstü Uygulaması)

Bu proje, Python Backend geliştirme serüvenimizin ilk basamağıdır. Temel amacımız; ilişkisel veritabanlarının (SQLite) nasıl çalıştığını anlamak, CRUD (Oluştur, Oku, Güncelle, Sil) işlemlerini uygulamak ve tüm bu arka plan mantığını (Backend) bir Masaüstü Arayüzü (GUI) ile entegre etmektir.

---

## 1. Mimari Kararlar: Neden İki Ayrı Dosya Yaptık?

Projeyi tek bir `main.py` dosyasına yazmak yerine `database.py` ve `main.py` olarak ikiye böldük. Bu yaklaşım yazılım mühendisliğinde **"Separation of Concerns" (Sorumlulukların Ayrılığı)** prensibinin en basit halidir.

* **`database.py` (Veri Katmanı - Model):** Sadece ve sadece veritabanı ile konuşur. Arayüzün nasıl göründüğü, butonların rengi veya pencereler umrunda değildir. 
* **`main.py` (Arayüz Katmanı - View/Controller):** Sadece pencereleri çizer ve kullanıcının butona basma olaylarını dinler. Veritabanının nasıl çalıştığını, SQL komutlarını bilmez; sadece `database.py` dosyasından yardım ister.

> [!TIP]
> **Daha Profesyonel Yaklaşım (MVC):** İlerleyen büyük projelerde bu yapıyı 3'e böleceğiz: **Model** (Veritabanı), **View** (Arayüz Şeması) ve **Controller** (İkisini konuşturan beyin). Şu anki yapımız, küçük projeler için ideal olan 2 katmanlı bir yapıdır.

---

## 2. Veritabanı Katmanı: `database.py` Analizi

Bu dosyada Python'ın standart kütüphanesi olan `sqlite3` kullandık.

### Temel Bağlantı Mantığı
```python
def baglanti_al():
    baglanti = sqlite3.connect("finans.db")
    baglanti.row_factory = sqlite3.Row 
    return baglanti
```
* `sqlite3.connect("finans.db")`: Eğer klasörde bu dosya yoksa sıfırdan oluşturur, varsa direkt bağlanır. 
* `row_factory = sqlite3.Row`: Normalde veritabanı sonuçları karmaşık listeler olarak döner. Bu komut, verileri bir Python sözlüğü (Dictionary) gibi `islem["tur"]` formatında okuyabilmemizi sağlar.

### Tablo Yaratmak
```python
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tur TEXT NOT NULL,
            miktar REAL NOT NULL,
...
```
* `CREATE TABLE IF NOT EXISTS`: Eğer tablo zaten varsa hata vermez, yoksa yaratır.
* `PRIMARY KEY AUTOINCREMENT`: Her veriye eşsiz (1, 2, 3...) bir kimlik verir. Silme ve Güncelleme işlemlerini bu ID üzerinden yaparız.
* `REAL`: SQL'de ondalıklı sayıları (Kuruşlu paraları) tutan veri tipidir.

### Veri Eklemek (SQL Injection Koruması)
```python
    imlec.execute(
        "INSERT INTO islemler (tur, miktar, aciklama, tarih) VALUES (?, ?, ?, ?)",
        (tur, miktar, aciklama, tarih)
    )
```
* Neden değişkenleri direkt yazmadık da `?` kullandık? Buna parametrik sorgu denir. Eğer kullanıcı açıklama kısmına kötü niyetli bir SQL komutu yazarsa (SQL Injection saldırısı), `?` işareti sayesinde veritabanı bunu bir kod olarak değil, zararsız bir "Metin" olarak algılar.

### Matematiksel Hesaplama (SUM)
```python
    imlec.execute("SELECT SUM(miktar) FROM islemler WHERE tur = 'Gelir'")
```
* **Profesyonel Yaklaşım:** Bakiye hesaplarken tüm verileri Python'a çekip `for` döngüsüyle toplamak (Python'da hesaplamak) amatörce bir yaklaşımdır. Matematik ve filtreleme işlemleri her zaman Veritabanı Motoru'na (SQL) yaptırılmalıdır. Veritabanları devasa verileri ışık hızında hesaplamak için tasarlanmıştır.

> [!IMPORTANT]
> **Daha Profesyonel Yaklaşım (ORM):** Biz burada "Saf (Raw) SQL" kullandık. İlerideki projelerde SQL komutlarını elle yazmak yerine, `SQLAlchemy` gibi ORM (Object-Relational Mapping) kütüphaneleri kullanacağız. ORM sayesinde hiç SQL bilmeden tamamen Python sınıflarıyla veritabanı yöneteceğiz.

---

## 3. Arayüz Katmanı: `main.py` Analizi

Bu dosyada arayüz kütüphanesi olarak `PyQt5` kullandık. Sektörde en çok tercih edilen profesyonel GUI motorlarından biridir.

### Nesne Yönelimli Programlama (OOP)
```python
class FinansUygulamasi(QWidget):
    def __init__(self):
        super().__init__()
```
* Kendi penceremizi oluşturmak için PyQt5'in `QWidget` sınıfından miras (inheritance) aldık. Böylece bizim sınıfımız otomatik olarak bir "Pencere" özelliklerine sahip oldu. `super().__init__()` ise üst sınıfın (QWidget) kendi ayarlarını başlatmasını sağlar.

### Geometri Yöneticileri (Layouts)
```python
        ana_duzen = QVBoxLayout()   # Dikey Düzen
        form_duzeni = QHBoxLayout() # Yatay Düzen
```
* Düğmeleri ekrana rastgele piksellerle (x=10, y=50) yerleştirmek (Absolute Positioning) amatörcedir; çünkü ekran boyutu değiştiğinde her şey bozulur.
* Bunun yerine `Box Layout` (Kutu Düzeni) kullanırız. `VBox` içine konan her şeyi alt alta dizer, `HBox` ise yan yana dizer. Biz ana pencereyi Dikey, Form kısmını Yatay düzenledik.

### Sinyaller ve Slotlar (Events)
```python
        kaydet_butonu.clicked.connect(self.veriyi_kaydet)
```
* Masaüstü uygulamaları "Event-Driven" (Olay güdümlü) çalışır. Uygulama sonsuz bir döngüde kullanıcının bir eylem yapmasını bekler. Burada `clicked` bir sinyaldir, onu bağladığımız fonksiyon (`self.veriyi_kaydet`) ise o sinyali karşılayan Slottur. 

### Veriyi UI (Arayüz) İle Bağlamak
```python
    def tabloyu_guncelle(self):
        veriler = database.tum_islemleri_getir()
```
* Arayüzümüz arka planda olanları bilmez. Biz arayüze "Git `database` dosyasındaki fonksiyonu çalıştır, oradan dönen cevabı alıp ekrana (Tabloya) çiz" diyoruz. Böylece arayüz temiz kalıyor.

> [!WARNING]
> **Daha Profesyonel Yaklaşım (Event Loop Bloklaması):** Şu anki uygulamamızda veritabanına veri yazılırken arayüz mikrosaniyeler seviyesinde "donar". Çünkü aynı "Thread" (İş Parçacığı) üzerinde çalışıyorlar. İleriki projelerde Veritabanı sorgularını "Asenkron" (Async) veya farklı bir Thread üzerinde çalıştırarak arayüzün asla donmamasını (Non-blocking) sağlayacağız.

---

## Sonuç
Bu ilk proje ile, verinin A noktasından (Kullanıcı Ekranı) çıkıp, B noktasında (Veritabanı Dosyası) kalıcı olarak saklanmasının tüm iskeletini inşa ettik. İlerideki projelerde sadece A ve B noktalarındaki teknolojiler değişecek (Örn: A ekranı bir Web Sayfası olacak, B veritabanı ise PostgreSQL olacak) ama **mantık hep aynı kalacak.**
