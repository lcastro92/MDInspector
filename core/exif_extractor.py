import io
from typing import Dict, Any
import exifread
from PIL import Image


def _convert_to_degrees(value) -> float:
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


def extract_image_metadata(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    metadata = {
        "filename": filename,
        "type": "image",
        "format": "Unknown",
        "dimensions": "Desconocido",
        "camera": "Desconocido",
        "software": "Desconocido",
        "datetime": "No registrada",
        "gps": None,
        "raw_exif": {}
    }

    try:
        # Obtener dimensiones y formato con Pillow sin cargar todos los píxeles
        with Image.open(io.BytesIO(file_bytes)) as img:
            metadata["format"] = img.format
            metadata["dimensions"] = f"{img.width} x {img.height} px"

        # Leer etiquetas EXIF con ExifRead
        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)

        if tags:
            make = str(tags.get("Image Make", ""))
            model = str(tags.get("Image Model", ""))
            if make or model:
                metadata["camera"] = f"{make} {model}".strip()

            metadata["software"] = str(tags.get("Image Software", "No especificado"))
            metadata["datetime"] = str(
                tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime") or "No registrada"
            )

            # Extracción GPS
            if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
                lat = _convert_to_degrees(tags["GPS GPSLatitude"])
                if str(tags.get("GPS GPSLatitudeRef", "N")) != "N":
                    lat = -lat

                lon = _convert_to_degrees(tags["GPS GPSLongitude"])
                if str(tags.get("GPS GPSLongitudeRef", "E")) != "E":
                    lon = -lon

                metadata["gps"] = {"latitude": lat, "longitude": lon}

            # Tags filtrados para la vista previa
            raw = {}
            for k, v in tags.items():
                if not k.startswith("JPEGThumbnail") and not k.startswith("TIFFThumbnail"):
                    raw[k] = str(v)
            metadata["raw_exif"] = raw

        return metadata
    except Exception as e:
        metadata["error"] = f"Error procesando la imagen: {str(e)}"
        return metadata
