from flask import Flask, request, jsonify, render_template
import requests
import yagmail
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
from bs4 import BeautifulSoup
import requests
import logging
import pywhatkit
# from flask import Flask, request, jsonify, send_file
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import io
# from flask import Flask, request, send_file, jsonify
# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import os

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')


# geting geo-location
def get_location():

    """
    Fetches the geographical location of the current IP address using the ipinfo.io API.

    :return: A dictionary containing the IP address, city, region, country, latitude, and longitude.
    """
    try:
        # Send a request to ipinfo.io to get location information
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status()  # Raise an exception for bad responses

        # Parse the response JSON
        data = response.json()

        # Extract geographical coordinates and location
        ip_address = data.get('ip')
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        location = data.get('loc').split(',')
        latitude = location[0]
        longitude = location[1]

        # Return the location information as a dictionary
        return {
            'ip_address': ip_address,
            'city': city,
            'region': region,
            'country': country,
            'latitude': latitude,
            'longitude': longitude
        }

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

@app.route('/location', methods=['GET'])
def location():
    location_info = get_location()
    return jsonify(location_info)










# sending an email
def send_email(subject, body, to_email, from_email="priyankapoonia803@gmail.com", app_password="gynn tyem qgwc alca"):
    try:
        yag = yagmail.SMTP(from_email, app_password)
        yag.send(to=to_email, subject=subject, contents=body)
        return {"status": "success", "message": "Email sent successfully!"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {e}"}

@app.route('/send_email', methods=['POST'])
def send_email_api():
    data = request.json
    subject = data.get('subject')
    body = data.get('body')
    to_email = data.get('to_email')
    from_email = data.get('from_email', "priyankapoonia803@gmail.com")
    app_password = data.get('app_password', "gynn tyem qgwc alca")

    result = send_email(subject, body, to_email, from_email, app_password)
    return jsonify(result)




# send bulk emails
def send_bulk_email(sender_email, sender_password, subject, message, recipients):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # SSL port for Gmail

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as smtp:
            smtp.login(sender_email, sender_password)

            for recipient in recipients:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                smtp.send_message(msg)
                print(f"Email sent to {recipient}")

        return {"status": "success", "message": f"Emails sent to {len(recipients)} recipients."}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/send_bulk_email', methods=['POST'])
def send_bulk_email_api():
    data = request.json

    sender_email = data.get('sender_email')
    sender_password = data.get('sender_password')
    subject = data.get('subject')
    message = data.get('message')
    recipients = data.get('recipients')

    if not all([sender_email, sender_password, subject, message, recipients]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    result = send_bulk_email(sender_email, sender_password, subject, message, recipients)
    return jsonify(result)





def get_volume():
    """
    Get the current system volume level.

    :return: The current volume level as a percentage (0.0 to 100.0).
    """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    return current_volume * 100  # Return as a percentage


# to set volume
def set_volume(level):
    """
    Set the system volume to a specified level.

    :param level: The desired volume level as a percentage (0.0 to 100.0).
    :return: A message indicating success or error.
    """
    if 0.0 <= level <= 100.0:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return {"status": "success", "message": f"Volume set to {level:.2f}%"}
    else:
        return {"status": "error", "message": "Volume level must be between 0.0 and 100.0"}

@app.route('/get_volume', methods=['GET'])
def get_volume_api():
    try:
        current_volume = get_volume()
        return jsonify({"status": "success", "current_volume": current_volume})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set_volume', methods=['POST'])
def set_volume_api():
    data = request.json
    level = data.get('level')

    if level is None or not isinstance(level, (int, float)):
        return jsonify({"status": "error", "message": "Please provide a valid volume level between 0 and 100."}), 400

    try:
        result = set_volume(level)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    



    # text to voice
def text_to_speech(text, lang='hi', filename='voice_note.mp3'):
    """
    Convert text to speech and save it as an audio file.

    :param text: The text to be converted to speech.
    :param lang: The language in which the text should be spoken (default is Hindi 'hi').
    :param filename: The name of the file to save the speech audio (default is 'voice_note.mp3').
    :return: The filename if successful, or an error message if failed.
    """
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang)
        
        # Save the audio file
        tts.save(filename)
        return filename
    except Exception as e:
        return str(e)

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech_api():
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'hi')
    filename = data.get('filename', 'voice_note.mp3')

    if not text:
        return jsonify({"status": "error", "message": "Text is required."}), 400

    try:
        saved_filename = text_to_speech(text, lang, filename)
        
        if saved_filename.endswith('.mp3'):
            return send_file(saved_filename, as_attachment=True)
        else:
            return jsonify({"status": "error", "message": saved_filename}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    



# top google search
    logging.basicConfig(level=logging.INFO)

def google_search(query, num_results=5):
    """
    Perform a Google search and return the top search results.

    :param query: The search query string.
    :param num_results: The number of search results to return (default is 5).
    :return: A list of dictionaries containing the title, link, and snippet of each result.
    """
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = []
        for result in soup.find_all('div', class_='tF2Cxc', limit=num_results):
            title_element = result.find('h3')
            link_element = result.find('a')
            snippet_element = result.find('span', class_='aCOpRe')

            title = title_element.text if title_element else 'No title available'
            link = link_element['href'] if link_element else 'No link available'
            snippet = snippet_element.text if snippet_element else 'No snippet available'

            search_results.append({
                'title': title,
                'link': link,
                'snippet': snippet
            })
        
        return search_results

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching results: {e}")
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")

    return None

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    num_results = request.args.get('num_results', default=5, type=int)

    if not query:
        return jsonify({"status": "error", "message": "Query parameter is required."}), 400

    results = google_search(query, num_results)
    
    if results:
        return jsonify({"status": "success", "results": results})
    else:
        return jsonify({"status": "error", "message": "Failed to retrieve search results."})
    


    # send whatsaap
    logging.basicConfig(level=logging.INFO)

def send_whatsapp_message(phone_number, message, hour, minute):
    """
    Send a WhatsApp message using pywhatkit.

    :param phone_number: Recipient's phone number in international format (e.g., "+918233120900").
    :param message: The content of the WhatsApp message.
    :param hour: The hour at which the message should be sent (24-hour format).
    :param minute: The minute at which the message should be sent.
    """
    try:
        # Send the WhatsApp message
        pywhatkit.sendwhatmsg(phone_number, message, hour, minute)
        return {"status": "success", "message": f"Message scheduled to be sent to {phone_number} at {hour}:{minute}."}
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp_api():
    data = request.json
    phone_number = data.get('phone_number')
    message = data.get('message')
    hour = data.get('hour')
    minute = data.get('minute')

    # Validate the input
    if not phone_number or not message or not isinstance(hour, int) or not isinstance(minute, int):
        return jsonify({"status": "error", "message": "Invalid input. Please provide phone_number, message, hour, and minute."}), 400

    try:
        result = send_whatsapp_message(phone_number, message, hour, minute)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    











# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# =====================================================================MACHINE LEARNING========================================================================================================================================================================================================================================================================================================
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







# # dataprocessing 
# def load_data(file_path):
#     try:
#         df = pd.read_csv(file_path)
#         return df
#     except Exception as e:
#         raise Exception(f"Error loading data: {e}")

# def clean_data(df):
#     try:
#         df = df.drop_duplicates()
#         numeric_cols = df.select_dtypes(include=[np.number]).columns
#         non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
#         df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
#         for col in non_numeric_cols:
#             df[col] = df[col].fillna(df[col].mode()[0])
#         return df
#     except Exception as e:
#         raise Exception(f"Error cleaning data: {e}")

# def analyze_data(df):
#     try:
#         analysis = {}
#         analysis['summary_statistics'] = df.describe(include='all').to_dict()
#         if not df.select_dtypes(include=[np.number]).empty:
#             analysis['correlation_matrix'] = df.corr().to_dict()
#         return analysis
#     except Exception as e:
#         raise Exception(f"Error analyzing data: {e}")

# def visualize_data(df):
#     try:
#         # Create a BytesIO buffer to save the plot image
#         buffer = io.BytesIO()

#         # Histogram of numeric columns
#         df.hist(figsize=(10, 8))
#         plt.suptitle('Histograms of Numeric Columns')
#         plt.savefig(buffer, format='png')
#         plt.close()

#         buffer.seek(0)
#         return buffer
#     except Exception as e:
#         raise Exception(f"Error visualizing data: {e}")

# @app.route('/process', methods=['POST'])
# def process_data():
#     try:
#         file = request.files['file']
#         file_path = f"/tmp/{file.filename}"
#         file.save(file_path)
        
#         df = load_data(file_path)
#         df = clean_data(df)
#         analysis = analyze_data(df)
#         buffer = visualize_data(df)
        
#         return jsonify({
#             'summary_statistics': analysis['summary_statistics'],
#             'correlation_matrix': analysis.get('correlation_matrix', {})
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @app.route('/download-plot', methods=['GET'])
# def download_plot():
#     try:
#         buffer = io.BytesIO()
#         df = pd.read_csv('/tmp/data.csv')  # Replace with actual path where the data is saved
#         buffer = visualize_data(df)
#         buffer.seek(0)
#         return send_file(buffer, as_attachment=True, attachment_filename='plot.png', mimetype='image/png')

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400




# # to apply filters
# def apply_filters(image_path):
#     """
#     Applies various filters to an image and saves the results.
    
#     Args:
#         image_path (str): The path to the image file.
#     """
#     image = cv2.imread(image_path)
#     if image is None:
#         return None

#     # Convert to RGB (from BGR) for displaying with matplotlib
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
#     # Apply filters
#     blur = cv2.GaussianBlur(image, (15, 15), 0)
#     grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(image, 100, 200)
    
#     kernel = np.array([[0.272, 0.534, 0.131],
#                        [0.349, 0.686, 0.168],
#                        [0.393, 0.769, 0.189]])
#     sepia = cv2.transform(image, kernel)
#     sepia = np.clip(sepia, 0, 255)
    
#     invert = cv2.bitwise_not(image)
    
#     # Save filtered images
#     results = {}
#     output_paths = {
#         'blur': 'static/blur.jpg',
#         'grayscale': 'static/grayscale.jpg',
#         'edges': 'static/edges.jpg',
#         'sepia': 'static/sepia.jpg',
#         'invert': 'static/invert.jpg'
#     }

#     cv2.imwrite(output_paths['blur'], blur)
#     cv2.imwrite(output_paths['grayscale'], grayscale)
#     cv2.imwrite(output_paths['edges'], edges)
#     cv2.imwrite(output_paths['sepia'], sepia)
#     cv2.imwrite(output_paths['invert'], invert)
    
#     return output_paths

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     """
#     Handles image upload and applies filters.
#     """
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if file:
#         file_path = os.path.join('static', 'uploaded_image.jpg')
#         file.save(file_path)
        
#         output_paths = apply_filters(file_path)
#         if output_paths:
#             return jsonify(output_paths)
#         else:
#             return jsonify({"error": "Error applying filters"}), 500

# @app.route('/download/<filter_name>', methods=['GET'])
# def download_image(filter_name):
#     """
#     Serves the filtered images for download.
#     """
#     if filter_name not in ['blur', 'grayscale', 'edges', 'sepia', 'invert']:
#         return jsonify({"error": "Invalid filter name"}), 400

#     file_path = f'static/{filter_name}.jpg'
#     if not os.path.exists(file_path):
#         return jsonify({"error": "File not found"}), 404

#     return send_file(file_path, as_attachment=True)






# # photo crop
# # Function to create a gradient image
# def create_gradient_image(width, height):
#     image = np.zeros((height, width, 3), dtype=np.uint8)
#     for y in range(height):
#         for x in range(width):
#             image[y, x] = [x % 256, 0, y % 256]  # BGR gradient from blue to red
#     output_path = 'static/gradient_image.png'
#     cv2.imwrite(output_path, image)
#     return output_path

# # Function to create a solid color image
# def create_solid_color_image(width, height, color):
#     image = np.zeros((height, width, 3), dtype=np.uint8)
#     image[:] = color  # BGR format
#     output_path = 'static/solid_color_image.png'
#     cv2.imwrite(output_path, image)
#     return output_path

# # Function to create a checkerboard image
# def create_checkerboard_image(width, height, square_size):
#     image = np.zeros((height, width, 3), dtype=np.uint8)
#     for y in range(0, height, square_size):
#         for x in range(0, width, square_size):
#             if (x // square_size) % 2 == (y // square_size) % 2:
#                 image[y:y+square_size, x:x+square_size] = [255, 255, 255]  # White squares
#     output_path = 'static/checkerboard_image.png'
#     cv2.imwrite(output_path, image)
#     return output_path

# # API route to generate the images
# @app.route('/generate_images', methods=['GET'])
# def generate_images():
#     try:
#         # Get image parameters from the request
#         width = int(request.args.get('width', 256))
#         height = int(request.args.get('height', 256))
#         solid_color = request.args.get('solid_color', '255,0,0').split(',')
#         solid_color = [int(c) for c in solid_color]
#         square_size = int(request.args.get('square_size', 32))

#         # Generate the images
#         gradient_path = create_gradient_image(width, height)
#         solid_color_path = create_solid_color_image(width, height, solid_color)
#         checkerboard_path = create_checkerboard_image(width, height, square_size)

#         # Return the image paths as JSON
#         return jsonify({
#             'gradient_image': gradient_path,
#             'solid_color_image': solid_color_path,
#             'checkerboard_image': checkerboard_path
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # API route to download the generated images
# @app.route('/download/<image_type>', methods=['GET'])
# def download_image(image_type):
#     # Map image types to filenames
#     image_files = {
#         'gradient_image': 'static/gradient_image.png',
#         'solid_color_image': 'static/solid_color_image.png',
#         'checkerboard_image': 'static/checkerboard_image.png'
#     }

#     # Check if the image_type is valid
#     if image_type not in image_files:
#         return jsonify({"error": "Invalid image type"}), 400

#     # Get the file path based on the image type
#     file_path = image_files[image_type]
    
#     # Check if the file exists
#     if not os.path.exists(file_path):
#         return jsonify({"error": "File not found"}), 404

#     # Send the file for download
#     return send_file(file_path, as_attachment=True)




# # selfie
# def capture_image():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Error: Could not open camera.")
#         return None
    
#     ret, frame = cap.read()
#     cap.release()
    
#     if not ret:
#         print("Error: Could not read frame.")
#         return None
    
#     return frame

# def detect_and_crop_face(image):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
#     if len(faces) == 0:
#         print("No faces detected.")
#         return None, None
    
#     x, y, w, h = faces[0]
#     face_image = image[y:y+h, x:x+w]
    
#     face_image_resized = cv2.resize(face_image, (300, 400))
    
#     return face_image_resized, (x, y, w, h)

# def overlay_face_on_image(image, face_image, face_coords):
#     x, y, w, h = face_coords
    
#     center_x, center_y = x + w // 2, y + h // 2
    
#     start_x = max(center_x - 150, 0)
#     start_y = max(center_y - 200, 0)
    
#     end_x = min(start_x + 300, image.shape[1])
#     end_y = min(start_y + 400, image.shape[0])
    
#     overlay_region = image[start_y:end_y, start_x:end_x]
    
#     overlay_region_resized = cv2.resize(face_image, (end_x - start_x, end_y - start_y))
    
#     image[start_y:end_y, start_x:end_x] = overlay_region_resized
    
#     return image

# @app.route('/capture_face', methods=['GET'])
# def capture_face():
#     image = capture_image()
#     if image is None:
#         return jsonify({"error": "Could not capture image"}), 500
    
#     face_image, face_coords = detect_and_crop_face(image)
#     if face_image is None:
#         return jsonify({"error": "No face detected"}), 404
    
#     result_image = overlay_face_on_image(image, face_image, face_coords)
    
#     output_path = 'static/result_image.png'
#     cv2.imwrite(output_path, result_image)
    
#     return send_file(output_path, mimetype='image/png')








if __name__ == '__main__':
    app.run(debug=True)