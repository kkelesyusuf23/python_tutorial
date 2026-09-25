import cv2
import mediapipe as mp
import numpy as np
import math
import time

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

canvas = None
xp, yp = 0, 0

# 3D Uzaydaki Objelerimizin Hafızası
kupler = [] # Her obje: {'x', 'y', 'z', 'size', 'rot_x', 'rot_y', 'id'}
cube_id_counter = 0

# ETKİLEŞİM (MANİPÜLASYON) HAFIZASI
secilen_kup_id = None
etkilesim_modu = None # 'Move' (Taşı), 'Scale' (Büyüt), 'Rotate' (Döndür)
ilk_cx, ilk_cy = 0, 0
ilk_deger = 0 

# ================= 1. 3D RENDER MOTORU =================
cube_vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
]
cube_edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

def render_3d_cube(img, cx, cy, cz, size, rot_x, rot_y, face_offset_x, face_offset_y, is_selected):
    drawn_pts = []
    for v in cube_vertices:
        # X ve Y eksenlerinde objeyi manuel döndürme matematiği
        x1 = v[0]*math.cos(rot_y) - v[2]*math.sin(rot_y)
        z1 = v[0]*math.sin(rot_y) + v[2]*math.cos(rot_y)
        y1 = v[1]
        
        y2 = y1*math.cos(rot_x) - z1*math.sin(rot_x)
        z2 = y1*math.sin(rot_x) + z1*math.cos(rot_x)
        x2 = x1
        
        parallax_x = face_offset_x * (z2 + 2) * 0.15
        parallax_y = face_offset_y * (z2 + 2) * 0.15
        
        px = int(cx + (x2 * size) + parallax_x)
        py = int(cy + (y2 * size) + parallax_y)
        drawn_pts.append((px, py))
        
    # Eğer küpü ellerimizle tutuyorsak rengini Kırmızı (Seçili) yap
    color = (0, 0, 255) if is_selected else (0, 255, 255)
    thickness = 6 if is_selected else 4
        
    for edge in cube_edges:
        pt1 = drawn_pts[edge[0]]
        pt2 = drawn_pts[edge[1]]
        cv2.line(img, pt1, pt2, color, thickness)
        
    # TUTMA KÖŞELERİ (Bounding Box & Corner Dots): Sadece seçiliyken görünür
    if is_selected:
        cv2.rectangle(img, (int(cx-size), int(cy-size)), (int(cx+size), int(cy+size)), (0, 255, 0), 2)
        cv2.circle(img, (int(cx-size), int(cy-size)), 15, (255, 0, 0), cv2.FILLED) 
        cv2.circle(img, (int(cx+size), int(cy-size)), 15, (255, 0, 0), cv2.FILLED) 
        cv2.circle(img, (int(cx-size), int(cy+size)), 15, (255, 0, 0), cv2.FILLED) 
        cv2.circle(img, (int(cx+size), int(cy+size)), 15, (255, 0, 0), cv2.FILLED) 

son_tiklama_zamani = 0

print("🥽 Apple Vision AR (V8.0 Interactive Physics Engine) Başlatıldı!")

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    
    if canvas is None:
        canvas = np.zeros_like(img)
        
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 2. YÜZ TAKİBİ
    face_x, face_y = 0, 0
    face_results = face_mesh.process(imgRGB)
    if face_results.multi_face_landmarks:
        burun = face_results.multi_face_landmarks[0].landmark[1]
        h, w, c = img.shape
        face_x, face_y = int(burun.x * w), int(burun.y * h)
        face_offset_x = face_x - (w//2)
        face_offset_y = face_y - (h//2)
    else:
        face_offset_x, face_offset_y = 0, 0

    # 3. EL TAKİBİ
    hand_results = hands.process(imgRGB)
    
    cimdik_var = False

    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            lmList = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy, lm.z]) 
                
            if len(lmList) != 0:
                x4, y4 = lmList[4][1], lmList[4][2] 
                x8, y8 = lmList[8][1], lmList[8][2] 
                x12, y12 = lmList[12][1], lmList[12][2]
                
                x5, y5 = lmList[5][1], lmList[5][2]
                x17, y17 = lmList[17][1], lmList[17][2]
                avuc_genisligi = math.hypot(x17 - x5, y17 - y5)
                tiklama_esigi = avuc_genisligi * 0.6
                
                mesafe_isaret = math.hypot(x8 - x4, y8 - y4)  
                mesafe_orta = math.hypot(x12 - x4, y12 - y4)  
                
                cursor_x, cursor_y = (x4 + x8) // 2, (y4 + y8) // 2
                
                # YUMRUK (Silgi)
                orta_parmak_kapali = lmList[12][2] > lmList[9][2]
                yuzuk_parmak_kapali = lmList[16][2] > lmList[13][2]
                serce_parmak_kapali = lmList[20][2] > lmList[17][2]
                yumruk = orta_parmak_kapali and yuzuk_parmak_kapali and serce_parmak_kapali
                
                if yumruk:
                    canvas = np.zeros_like(img)
                    kupler.clear()
                    secilen_kup_id = None
                    cv2.putText(img, 'UZAY SIFIRLANDI!', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    xp, yp = 0, 0
                    
                # ================= GESTURE: 3D KÜP EKLE (Tuz Atma) =================
                elif mesafe_isaret < tiklama_esigi and mesafe_orta < tiklama_esigi:
                    cv2.circle(img, (cursor_x, cursor_y), 15, (0, 255, 255), cv2.FILLED)
                    
                    su_an = time.time()
                    if su_an - son_tiklama_zamani > 1.0:
                        cz = lmList[8][3]
                        # Yeni bir objeyi uzaya kayıt et
                        kupler.append({'x': cursor_x, 'y': cursor_y, 'z': cz, 'size': int(avuc_genisligi * 0.8), 'rot_x': 0, 'rot_y': 0, 'id': cube_id_counter})
                        cube_id_counter += 1
                        son_tiklama_zamani = su_an
                    xp, yp = 0, 0
                        
                # ================= GESTURE: ÇİMDİK (2D Çizim veya 3D Manipülasyon) =================
                elif mesafe_isaret < tiklama_esigi and mesafe_orta >= tiklama_esigi:
                    cimdik_var = True
                    cv2.circle(img, (cursor_x, cursor_y), 15, (0, 255, 0), cv2.FILLED)
                    
                    # Eğer parmağımızda bir obje YOKA, boşluğu mu tuttuk yoksa bir küpü mü tuttuk diye kontrol et (Hit Detection)
                    if secilen_kup_id is None:
                        carpisma_oldu_mu = False
                        # Hangi objenin Bounding Box (Kutu sınırları) içerisindeyiz?
                        for kup in reversed(kupler):
                            kx, ky, ksize = kup['x'], kup['y'], kup['size']
                            if kx - ksize < cursor_x < kx + ksize and ky - ksize < cursor_y < ky + ksize:
                                carpisma_oldu_mu = True
                                secilen_kup_id = kup['id']
                                ilk_cx, ilk_cy = cursor_x, cursor_y
                                
                                # Acaba küpün neresinden tuttu? (Merkez, Köşe, Kenar)
                                dist_to_center = math.hypot(cursor_x - kx, cursor_y - ky)
                                
                                if dist_to_center < ksize * 0.4:
                                    etkilesim_modu = 'Move' # Merkezinden tutarsa Sürükler
                                elif abs(cursor_x - kx) > ksize * 0.7 and abs(cursor_y - ky) > ksize * 0.7:
                                    etkilesim_modu = 'Scale' # Kırmızı köşelerden tutarsa Büyütür
                                    ilk_deger = ksize
                                else:
                                    etkilesim_modu = 'Rotate' # Kenarlardan tutarsa Döndürür
                                    ilk_deger = (kup['rot_x'], kup['rot_y'])
                                break
                        
                        # Eğer hiçbir küpe değmeden çimdik attıysa, bil ki uzayda 2D yazı yazmak istiyor.
                        if not carpisma_oldu_mu:
                            secilen_kup_id = -1 # "-1" bizim için 2D Çizim Modunu temsil eder
                            
                    # ================= FİZİK İŞLEMLERİ =================
                    if secilen_kup_id == -1: 
                        # Boşluktayız, mor çizgi çiz!
                        if xp == 0 and yp == 0:
                            xp, yp = cursor_x, cursor_y
                        cv2.line(canvas, (xp, yp), (cursor_x, cursor_y), (255, 0, 255), 15)
                        xp, yp = cursor_x, cursor_y
                        
                    elif secilen_kup_id is not None: 
                        # Bir 3D Küpü tuttuk! Seçili küpe fiziksel baskı (Manipulation) uygula
                        for kup in kupler:
                            if kup['id'] == secilen_kup_id:
                                if etkilesim_modu == 'Move':
                                    kup['x'] = cursor_x
                                    kup['y'] = cursor_y
                                    cv2.putText(img, 'OBJEYI TASIYORSUN', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                elif etkilesim_modu == 'Scale':
                                    diff_y = ilk_cy - cursor_y # Parmağını yukarı kaydırırsa obje büyür
                                    kup['size'] = max(20, ilk_deger + diff_y)
                                    cv2.putText(img, 'OBJEYI BUYUTUYORSUN', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                elif etkilesim_modu == 'Rotate':
                                    diff_x = cursor_x - ilk_cx
                                    diff_y = cursor_y - ilk_cy
                                    kup['rot_y'] = ilk_deger[1] + (diff_x * 0.02)
                                    kup['rot_x'] = ilk_deger[0] + (diff_y * 0.02)
                                    cv2.putText(img, 'OBJEYI DONDURUYORSUN', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                else:
                    # GEZİNME (Hover)
                    xp, yp = 0, 0
                    cv2.circle(img, (cursor_x, cursor_y), 15, (255, 0, 255), 2)
                    
    else:
        xp, yp = 0, 0
        
    # Parmağını açtığında (Çimdiği bıraktığında) objeyi havaya geri sal
    if not cimdik_var:
        secilen_kup_id = None
        etkilesim_modu = None

    # ================= 4. HOLOGRAMLARI RENDER ET =================
    for kup in kupler:
        is_sel = (kup['id'] == secilen_kup_id)
        # Eğer bir obje kimse tarafından tutulmuyorsa, havada Matrix gibi kendi ekseninde çok yavaşça dönmeye devam eder
        if not is_sel:
            kup['rot_y'] += 0.01 
            kup['rot_x'] += 0.01 
        render_3d_cube(img, kup['x'], kup['y'], kup['z'], kup['size'], kup['rot_x'], kup['rot_y'], face_offset_x, face_offset_y, is_sel)

    # ================= 5. AR BİRLEŞTİRME =================
    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, canvas)
    
    cv2.imshow("Apple Vision - V8.0 Interactive Physics Engine", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == 27:
        break
        
cap.release()
cv2.destroyAllWindows()
