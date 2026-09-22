from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem
from kivy.core.window import Window
import requests

# Mobil cihaz görünümü simülasyonu
Window.size = (350, 600)

KV = '''
ScreenManager:
    LoginScreen:
    RegisterScreen:
    NotesScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            text: "Kilitli Sepet"
            font_style: "H3"
            halign: "center"
            theme_text_color: "Primary"
            size_hint_y: None
            height: self.texture_size[1]
            
        MDTextField:
            id: username
            hint_text: "Kullanıcı Adı"
            icon_right: "account"
            
        MDTextField:
            id: password
            hint_text: "Şifre"
            password: True
            icon_right: "key-variant"
            
        MDRaisedButton:
            text: "Giriş Yap"
            pos_hint: {"center_x": 0.5}
            on_release: root.giris_yap()
            
        MDTextButton:
            text: "Hesabın yok mu? Kayıt Ol"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "register"
            
        MDLabel:
            id: mesaj
            text: ""
            theme_text_color: "Error"
            halign: "center"

<RegisterScreen>:
    name: "register"
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            text: "Kayıt Ol"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            
        MDTextField:
            id: reg_username
            hint_text: "Kullanıcı Adı"
            
        MDTextField:
            id: reg_password
            hint_text: "Şifre"
            password: True
            
        MDRaisedButton:
            text: "Kaydı Tamamla"
            pos_hint: {"center_x": 0.5}
            on_release: root.kayit_ol()
            
        MDTextButton:
            text: "Geri Dön"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "login"
            
        MDLabel:
            id: reg_mesaj
            text: ""
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            halign: "center"

<NotesScreen>:
    name: "notes"
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Gizli Notlarım"
            right_action_items: [["logout", lambda x: app.cikis_yap()]]
            
        ScrollView:
            MDList:
                id: notes_list
                
        MDBoxLayout:
            size_hint_y: None
            height: "80dp"
            padding: "10dp"
            spacing: "10dp"
            
            MDTextField:
                id: not_baslik
                hint_text: "Notunuzu yazın..."
                
            MDFloatingActionButton:
                icon: "plus"
                on_release: root.not_ekle()
'''

API_URL = "http://127.0.0.1:8000"

class LoginScreen(Screen):
    def giris_yap(self):
        kullanici = self.ids.username.text
        sifre = self.ids.password.text
        
        if not kullanici or not sifre:
            self.ids.mesaj.text = "Lütfen alanları doldurun!"
            return
            
        # OAuth2 form verisi olarak gönderiyoruz (FastAPI böyle bekliyor)
        data = {"username": kullanici, "password": sifre}
        try:
            cevap = requests.post(f"{API_URL}/giris", data=data)
            if cevap.status_code == 200:
                # 1. BİLETİ (TOKEN) AL!
                token = cevap.json().get("access_token")
                # 2. BİLETİ UYGULAMANIN HAFIZASINA KOY!
                MDApp.get_running_app().token = token
                self.ids.mesaj.text = ""
                # 3. NOTLAR SAYFASINA GEÇ VE İSTEK AT
                self.manager.current = "notes"
                self.manager.get_screen("notes").notlari_getir()
            else:
                self.ids.mesaj.text = "Kullanıcı adı veya şifre hatalı!"
        except Exception:
            self.ids.mesaj.text = "Sunucuya bağlanılamadı!"

class RegisterScreen(Screen):
    def kayit_ol(self):
        kullanici = self.ids.reg_username.text
        sifre = self.ids.reg_password.text
        
        if not kullanici or not sifre:
            self.ids.reg_mesaj.text = "Boş alan bırakmayın!"
            return
            
        json_data = {"kullanici_adi": kullanici, "sifre": sifre}
        try:
            cevap = requests.post(f"{API_URL}/kayit", json=json_data)
            if cevap.status_code == 200:
                self.ids.reg_mesaj.text = "Başarılı! Şimdi giriş yapabilirsiniz."
            else:
                hata = cevap.json().get("detail", "Kayıt başarısız")
                self.ids.reg_mesaj.text = hata
        except Exception:
            self.ids.reg_mesaj.text = "Sunucuya bağlanılamadı!"

class NotesScreen(Screen):
    def notlari_getir(self):
        token = MDApp.get_running_app().token
        if not token:
            return
            
        # KRİTİK NOKTA: BİLETİ (TOKEN) SUNUCUYA SUNUYORUZ! (Authorization Header)
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            cevap = requests.get(f"{API_URL}/notlar", headers=headers)
            if cevap.status_code == 200:
                notlar = cevap.json()
                self.ids.notes_list.clear_widgets()
                for n in notlar:
                    self.ids.notes_list.add_widget(
                        OneLineListItem(text=n["baslik"])
                    )
        except Exception:
            pass

    def not_ekle(self):
        token = MDApp.get_running_app().token
        baslik = self.ids.not_baslik.text
        
        if not baslik or not token:
            return
            
        # YİNE KRİTİK NOKTA: Token yoksa not ekleyemezsin!
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"baslik": baslik, "icerik": "Boş içerik"}
        
        try:
            cevap = requests.post(f"{API_URL}/notlar", json=json_data, headers=headers)
            if cevap.status_code == 200:
                self.ids.not_baslik.text = ""
                self.notlari_getir()
        except Exception:
            pass

class NotSepetiApp(MDApp):
    # Uygulamanın en tepesindeki değişken, kullanıcının bileti!
    token = None 

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        return Builder.load_string(KV)
        
    def cikis_yap(self):
        # Çıkış yaparken bileti yırtıp atıyoruz
        self.token = None
        self.root.current = "login"
        self.root.get_screen("login").ids.username.text = ""
        self.root.get_screen("login").ids.password.text = ""

if __name__ == "__main__":
    NotSepetiApp().run()
