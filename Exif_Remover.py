from flask import Flask, render_template, request
from PIL import Image
import os
import time
import subprocess
import glob

app = Flask(__name__, static_url_path='/static')

EXIFTOOL_PATH =  "C:\\Program Files\\exiftool\\exiftool.exe"  

def remove_exif(image_file):
    image = Image.open(image_file)
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    new_filename = "ex_" + os.path.basename(image_file)
    new_filepath = os.path.join(os.getcwd(), new_filename)
    image_without_exif.save(new_filepath)
    return new_filepath

def remove_exif_from_folder(folder_path):
    processed_files = []
    image_files = glob.glob(os.path.join(folder_path, '*.jpg')) + \
              glob.glob(os.path.join(folder_path, '*.jpeg')) + \
              glob.glob(os.path.join(folder_path, '*.png')) + \
              glob.glob(os.path.join(folder_path, '*.tif')) + \
              glob.glob(os.path.join(folder_path, '*.tiff')) + \
              glob.glob(os.path.join(folder_path, '*.gif')) + \
              glob.glob(os.path.join(folder_path, '*.webp')) + \
              glob.glob(os.path.join(folder_path, '*.arw')) + \
              glob.glob(os.path.join(folder_path, '*.cr2')) + \
              glob.glob(os.path.join(folder_path, '*.nef')) + \
              glob.glob(os.path.join(folder_path, '*.dng')) + \
              glob.glob(os.path.join(folder_path, '*.crw')) + \
              glob.glob(os.path.join(folder_path, '*.orf')) + \
              glob.glob(os.path.join(folder_path, '*.rw2')) + \
              glob.glob(os.path.join(folder_path, '*.sr2')) + \
              glob.glob(os.path.join(folder_path, '*.heif')) + \
              glob.glob(os.path.join(folder_path, '*.heic'))

    for image_file in image_files:
        try:
            processed_filename = remove_exif(image_file)
            processed_files.append(processed_filename)
            time.sleep(1)
        except Exception as e:
            processed_files.append(f"Error processing file {image_file}: {e}")
            app.logger.error(f"Error processing file {image_file}: {e}")
    return processed_files

def embed_file(image_path, file_to_embed, output_image, passphrase):
    try:
        subprocess.run(["steghide", "embed", "-ef", file_to_embed, "-cf", image_path, "-sf", output_image, "-p", passphrase], check=True)
        message = "File embedded successfully!"
    except subprocess.CalledProcessError as e:
        message = f"Error: {e}"
    return message

def extract_embedded_file(image_path, output_file, passphrase):
    try:
        subprocess.run(["steghide", "extract", "-sf", image_path, "-xf", output_file, "-p", passphrase], check=True)
        message = "Embedded file extracted successfully!"
    except subprocess.CalledProcessError as e:
        message = f"Error: {e}"
    return message


def view_metadata(file_path):
    try:
        if not os.path.exists(EXIFTOOL_PATH):
            raise FileNotFoundError(f"ExifTool not found at: {EXIFTOOL_PATH}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        result = subprocess.run([EXIFTOOL_PATH, file_path], capture_output=True, text=True)
        metadata = result.stdout
    except Exception as e:
        metadata = f"Error: {e}"
        app.logger.error(metadata)
    
    return metadata

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        action = request.form.get('action')
        passphrase = request.form.get('passphrase')
        if action == 'remove_exif_folder':
            folder_path = request.form.get('folder_path')
            if folder_path:
                processed_files = remove_exif_from_folder(folder_path)
                return render_template('upload.html', success_message="EXIF data removed successfully from all images!", request=request)
            else:
                return render_template('upload.html', error_message="Please provide a valid folder path.", request=request)
        else:
            files = request.files.getlist('file')
            processed_files = []
            for file in files:
                filename = file.filename
                if filename != '':
                    file.save(filename)
                    try:
                        if action == 'remove_exif':
                            processed_filename = remove_exif(filename)
                        elif action == 'embed':
                            file_to_embed = request.files.get('file_to_embed')
                            if file_to_embed:
                                file_to_embed.save(file_to_embed.filename)
                                processed_filename = embed_file(filename, file_to_embed.filename, f"embedded_{filename}", passphrase)
                                os.remove(file_to_embed.filename)
                            else:
                                processed_filename = "Error: No file to embed provided"
                        elif action == 'extract':
                            output_file = request.form.get('output_file_extract')
                            processed_filename = extract_embedded_file(filename, output_file, passphrase)
                        elif action == 'view_metadata':
                            metadata = view_metadata(filename)
                            return render_template('metadata.html', metadata=metadata)
                        processed_files.append(processed_filename)
                        time.sleep(1)
                    except Exception as e:
                        processed_files.append(f"Error processing file {filename}: {e}")
                        app.logger.error(f"Error processing file {filename}: {e}")
                    finally:
                        try:
                            os.remove(filename)
                        except Exception as e:

                            print(f"Error removing file {filename}: {e}")
                            if hasattr(e, 'winerror') and e.winerror == 32:
                                print(f"File {filename} is in use by another process. Skipping removal.")
                            else:
                                raise e  
            return render_template('upload.html', success_message="Files processed successfully!", request=request)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)