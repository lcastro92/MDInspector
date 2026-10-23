import io
from PIL import Image
import pypdf


def sanitize_image(file_bytes: bytes) -> bytes:
    """Remueve etiquetas EXIF exportando una copia limpia de los píxeles."""
    with Image.open(io.BytesIO(file_bytes)) as img:
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        
        output = io.BytesIO()
        fmt = img.format if img.format in ["JPEG", "PNG", "WEBP"] else "JPEG"
        clean_img.save(output, format=fmt)
        return output.getvalue()


def sanitize_pdf(file_bytes: bytes) -> bytes:
    """Crea una copia del PDF removiendo el diccionario /Info de metadatos."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Sobrescribir metadatos con valores neutros vacíos
    writer.add_metadata({})

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
