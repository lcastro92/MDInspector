import io
import pillow_heif
from PIL import Image, ExifTags

# Registrar soporte HEIC/HEIF en Pillow
pillow_heif.register_heif_opener()


def _convert_to_degrees(value):
    """Convierte coordenadas EXIF (grados, minutos, segundos) a grados decimales."""
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None


def extract_image_metadata(file_bytes: bytes, filename: str) -> dict:
    image = Image.open(io.BytesIO(file_bytes))

    dimensions = f"{image.width} x {image.height} px"
    fmt = (
        image.format
        or ("HEIC" if filename.lower().endswith((".heic", ".heif")) else "UNKNOWN")
    )

    camera = "Desconocido"
    datetime_str = "No registrada"
    software = "Desconocido"
    gps_data = None
    raw_exif = {}

    exif = image.getexif()
    if exif:
        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            raw_exif[tag_name] = str(value)

            if tag_name == "Make":
                camera = str(value)
            elif tag_name == "Model":
                camera = (
                    f"{camera} {value}".strip()
                    if camera != "Desconocido"
                    else str(value)
                )
            elif tag_name == "DateTime":
                datetime_str = str(value)
            elif tag_name == "Software":
                software = str(value)

        # Extraer SubIFD para datos GPS
        gps_info = (
            exif.get_ifd(ExifTags.Base.GPSInfo)
            if hasattr(ExifTags.Base, "GPSInfo")
            else {}
        )
        if gps_info:
            gps_tags = {}
            for key, val in gps_info.items():
                name = ExifTags.GPSTAGS.get(key, str(key))
                gps_tags[name] = val

            lat_ref = gps_tags.get("GPSLatitudeRef")
            lat = gps_tags.get("GPSLatitude")
            lon_ref = gps_tags.get("GPSLongitudeRef")
            lon = gps_tags.get("GPSLongitude")

            if lat and lon and lat_ref and lon_ref:
                lat_dec = _convert_to_degrees(lat)
                lon_dec = _convert_to_degrees(lon)
                if lat_dec is not None and lon_dec is not None:
                    if lat_ref != "N":
                        lat_dec = -lat_dec
                    if lon_ref != "E":
                        lon_dec = -lon_dec
                    gps_data = {
                        "latitude": round(lat_dec, 6),
                        "longitude": round(lon_dec, 6),
                    }

    return {
        "filename": filename,
        "type": "image",
        "format": fmt,
        "dimensions": dimensions,
        "camera": camera,
        "datetime": datetime_str,
        "software": software,
        "gps": gps_data,
        "raw_exif": raw_exif,
    }
