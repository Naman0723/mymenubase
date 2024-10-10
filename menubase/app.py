from flask import Flask, request, jsonify, render_template
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/project.html')
def project():
    return render_template('project.html')


if __name__ == "__main__":
    app.run(port=500, host="0.0.0.0")
