import pdfplumber
import re
from datetime import datetime

pdf_path = r"C:\Users\Gabriela\Documents\Nueva carpeta\Nueva carpeta\Nueva carpeta\codigos\entre_rios\Ret DGR Entre Rios 12.2025.pdf"
txt_salida = "dgr_entre_rios_12_2025.txt"

registros = []
orden = 1
cuit_actual = None

def num(txt):
    return float(txt.replace(".", "").replace(",", "."))

with pdfplumber.open(pdf_path) as pdf:
    texto = "\n".join(page.extract_text() or "" for page in pdf.pages)

lineas = [l.strip() for l in texto.split("\n") if l.strip()]

for linea in lineas:

    # ========= CUIT =========
    m_cuit = re.search(r"\d{2}-\d{8}-\d", linea)
    if m_cuit:
        cuit_actual = m_cuit.group().replace("-", "")
        continue

    # ========= LINEA DE COMPROBANTE (OBLIGATORIO TENER FECHA) =========
    m = re.search(r"(\d{2}/\d{2}/\d{2}).*?-\s*0*(\d+)\s*-", linea)
    if not m:
        continue  # descartamos totales y líneas sin fecha

    fecha = datetime.strptime(m.group(1), "%d/%m/%y")
    comprobante = m.group(2).zfill(12)

    # Tomamos SOLO los importes de esta línea
    nums = re.findall(r"-?[\d\.]+,\d{2}", linea)

    if len(nums) < 2:
        continue

    # En estas líneas: último = retenido, anteúltimo = base
    base = num(nums[-2])
    retenido = abs(num(nums[-1]))
    alicuota = round((retenido / base) * 100, 2)

    registros.append({
        "fecha": fecha,
        "linea": (
            f"{{orden}},1,1,{comprobante},{cuit_actual},"
            f"{fecha.strftime('%d/%m/%Y')},{base:.2f},{alicuota:.2f},{retenido:.2f},004,908"
        )
    })

# ========= ORDENAMOS POR FECHA =========
registros.sort(key=lambda x: x["fecha"])

# ========= ESCRIBIMOS TXT =========
with open(txt_salida, "w", encoding="utf-8") as f:
    for i, r in enumerate(registros, start=1):
        f.write(r["linea"].format(orden=f"{i:05d}") + "\n")

print(f"✅ Generado {len(registros)} registros (ordenados por fecha) → {txt_salida}")


# Verificar las alicuotas, puede pasar que las calcule mal.