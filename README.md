# Privacy-Enhancing Tool
A Python-based web tool to enhance image privacy by removing EXIF metadata and embedding/extracting files using steganography.

# Features
- Remove EXIF metadata from single images or entire folders
- View detailed image metadata via ExifTool
- Embed files securely into images with a passphrase
- Extract embedded files from images
- Supports multiple image formats: JPEG, PNG, TIFF, GIF, WebP, RAW

# Tech Stack / Skills
- Python
- Flask (Web Interface)
- PIL / Pillow (Image Processing)
- Steghide (Steganography)
- ExifTool (Metadata Extraction)
- File I/O / Folder Handling
- Web Security & Privacy Awareness

# How to Run
1. Clone the repository
2. Install dependencies:
   pip install flask pillow
3. Ensure Steghide and ExifTool are installed and their paths configured
4. Run the app:
   python app.py
5. Open your browser:
   http://127.0.0.1:5000

# Disclaimer
This project is for educational and personal privacy purposes only. 
Use only on files you own or have permission to manipulate.
