import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

app = FastAPI()

# MİMARİ NOTU: Tarayıcının hafızasını (Session/Çerez) şifreli tutmak için Gizli Anahtar.
# Bu sayede adamın biri çerezlerini (Cookies) değiştirip "Ben Adminim" diyemez.
app.add_middleware(SessionMiddleware, secret_key="cok_gizli_super_sifre")

templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. OAUTH VE GITHUB KİMLİKLERİ
# ==========================================
# Kullanıcının ilettiği o sihirli "Client ID" ve "Client Secret" buraya yazılır.
# Bunlar sitemizin (FastAPI) GitHub yanındaki resmi kimliğidir.
oauth = OAuth()
oauth.register(
    name='github',
    client_id='Ov23liWtU4PLVAUjup3n',
    client_secret='41c314a409bac209ae2ddea326a67ca86082436b',
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}, # Sadece kullanıcının mailini ve profilini istiyoruz (Depolarına karışmıyoruz)
)


# ==========================================
# 2. ROTALAR (GİRİŞ - ÇIKIŞ SİSTEMİ)
# ==========================================

@app.get("/")
async def anasayfa(request: Request):
    # Eğer tarayıcı hafızasında (Session) zaten 'user' varsa, bir daha şifre sorma, direkt içeri al.
    kullanici = request.session.get('user')
    if kullanici:
        return RedirectResponse(url='/dashboard')
    
    # Yoksa, "GitHub ile Giriş" butonunun olduğu ana sayfayı göster.
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login(request: Request):
    # 1. AŞAMA: Tıklandığında kullanıcıyı GitHub'ın şifre girme ekranına fırlat.
    # Kullanıcı şifresini GitHub'a girecek (Biz asla şifresini görmeyeceğiz, çok güvenli!)
    # Giriş yapınca bizi geri nereye fırlatacak? -> "/auth" rotasına
    redirect_uri = request.url_for('auth')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth(request: Request):
    # 2. AŞAMA: Kullanıcı şifreyi girip GitHub tarafından sitemize Geri Fırlatıldı (Callback).
    # GitHub gelirken elinde gizli bir "Token (Jeton)" getirdi. Onu alalım:
    token = await oauth.github.authorize_access_token(request)
    
    # O jeton ile hemen GitHub'ın veritabanına gidip "Bu jetonun sahibi kim?" diye soralım:
    resp = await oauth.github.get('user', token=token)
    profile = resp.json()
    
    # 3. AŞAMA: Kullanıcının profilini (Adını, resmini) sitemizin Session (Hafıza) bölümüne kaydet.
    # Artık adam sekmesini kapatsa bile sitede giriş yapmış sayılacak.
    request.session['user'] = profile
    
    return RedirectResponse(url='/dashboard')


@app.get("/dashboard")
async def dashboard(request: Request):
    kullanici = request.session.get('user')
    # Hafızada kullanıcı yoksa, ana sayfaya (login) geri kovala (Kaçak giriş engeli)
    if not kullanici:
        return RedirectResponse(url='/')
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": kullanici})


@app.get("/logout")
async def logout(request: Request):
    # Çıkış yaparken tarayıcıdaki gizli hafızayı (user) silip çöpe at
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
