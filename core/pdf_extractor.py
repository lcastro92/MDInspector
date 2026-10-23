import io
from typing import Dict, Any
import pypdf


def extract_pdf_metadata(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    metadata = {
        "filename": filename,
        "type": "pdf",
        "page_count": 0,
        "title": "Sin título",
        "author": "Desconocido",
        "producer": "Desconocido",
        "creation_date": "No registrada",
        "encrypted": False,
        "raw_metadata": {}
    }

    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        metadata["page_count"] = len(reader.pages)
        metadata["encrypted"] = reader.is_encrypted

        info = reader.metadata
        if info:
            metadata["title"] = info.title if info.title else "Sin título"
            metadata["author"] = info.author if info.author else "Desconocido"
            metadata["producer"] = info.producer if info.producer else "Desconocido"
            metadata["creation_date"] = str(info.creation_date) if info.creation_date else "No registrada"

            raw = {}
            for k, v in info.items():
                clean_key = k.replace("/", "")
                raw[clean_key] = str(v)
            metadata["raw_metadata"] = raw

        return metadata
    except Exception as e:
        metadata["error"] = f"Error al inspeccionar PDF: {str(e)}"
        return metadata
