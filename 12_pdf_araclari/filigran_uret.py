from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color

def uret():
    c = canvas.Canvas("filigran.pdf", pagesize=A4)
    # Merkeze al
    c.translate(A4[0] / 2.0, A4[1] / 2.0)
    # Kırmızı renk ve yarı saydam (alpha=0.3)
    c.setFillColor(Color(0.8, 0.2, 0.2, alpha=0.3))
    c.setFont("Helvetica-Bold", 80)
    # 45 derece döndür
    c.rotate(45)
    # Tam ortaya GİZLİDİR yaz
    c.drawCentredString(0, 0, "GIZLIDIR")
    c.save()
    print("filigran.pdf basariyla uretildi.")

if __name__ == "__main__":
    uret()
