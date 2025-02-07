import pytesseract
from PIL import Image

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/home/darling/Documents/audity/lib/python3.13/site-packages/tesseract/'  # Update this path if necessary

# Test Tesseract with an image
try:
    # Load an image file
    image = Image.open('/home/darling/Documents/audity/WhatsApp Image 2025-02-04 at 7.26.59 PM.jpeg')  # Replace with your image file path
    text = pytesseract.image_to_string(image)
    print("Extracted Text:", text)
except pytesseract.TesseractNotFoundError as e:
    print("Tesseract not found. Please check the installation and path.")
except Exception as e:
    print("An error occurred:", e)