# proyecto2/visual/report_generator.py

from fpdf import FPDF
import os

# Ruta destino del PDF generado
OUTPUT_PATH = "proyecto2/visual/generated_report.pdf"

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Informe del Sistema Logístico de Drones", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generate():
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    # Simulación de datos de informe
    pdf.cell(0, 10, "Rutas más frecuentes:", ln=True)
    pdf.cell(0, 10, "- A → B → C (5 veces)", ln=True)
    pdf.cell(0, 10, "- A → D → E (3 veces)", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Clientes más recurrentes:", ln=True)
    pdf.cell(0, 10, "- Ricardo Rios (12 visitas)", ln=True)
    pdf.cell(0, 10, "- Valeria Soto (9 visitas)", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Nodos más utilizados:", ln=True)
    pdf.cell(0, 10, "- Nodo 101 (almacenamiento): 25 visitas", ln=True)
    pdf.cell(0, 10, "- Nodo 201 (recarga): 20 visitas", ln=True)

    # Guardar archivo PDF
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    pdf.output(OUTPUT_PATH)
    return OUTPUT_PATH
