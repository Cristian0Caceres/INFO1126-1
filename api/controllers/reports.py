# proyecto2/api/controllers/reports.py

from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import FileResponse
import os
from visual import report_generator

router = APIRouter()

@router.get("/pdf")
def generate_report_pdf():
    try:
        # Genera el PDF usando el módulo existente
        pdf_path = report_generator.generate()

        # Verifica que el archivo exista antes de enviarlo
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="No se pudo generar el informe PDF.")

        return FileResponse(pdf_path, media_type="application/pdf", filename="informe_rutas.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
