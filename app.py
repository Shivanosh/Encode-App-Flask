import string
import random
import json
import os
from flask import Flask, request, render_template, send_file, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_encryption_key():
    characters = string.ascii_letters + string.digits + string.punctuation + ' '
    shuffled_characters = list(characters)
    random.shuffle(shuffled_characters)
    shuffled_characters = ''.join(shuffled_characters)
    
    encryption_key = dict(zip(characters, shuffled_characters))
    return encryption_key

def encode(text, key):
    return ''.join(key.get(char, char) for char in text)

def decode(text, key):
    return ''.join(key.get(char, char) for char in text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_key', methods=['POST'])
def generate_key():
    encryption_key = create_encryption_key()
    key_filename = os.path.join(UPLOAD_FOLDER, 'encryption_key.json')
    with open(key_filename, 'w') as file:
        json.dump(encryption_key, file)
    return send_file(key_filename, as_attachment=True)

@app.route('/upload_key', methods=['POST'])
def upload_key():
    file = request.files['key_file']
    key_filepath = os.path.join(UPLOAD_FOLDER, 'encryption_key.json')
    file.save(key_filepath)
    return redirect(url_for('decode_message'))

@app.route('/encode', methods=['GET', 'POST'])
def encode_message():
    if request.method == 'POST':
        text = request.form['text']
        key_filepath = os.path.join(UPLOAD_FOLDER, 'encryption_key.json')
        if os.path.exists(key_filepath):
            with open(key_filepath, 'r') as file:
                encryption_key = json.load(file)
            encoded_text = encode(text, encryption_key)
            encoded_filename = os.path.join(UPLOAD_FOLDER, 'encoded_message.txt')
            with open(encoded_filename, 'w') as file:
                file.write(encoded_text)
            return send_file(encoded_filename, as_attachment=True)
        else:
            return "Encryption key not found. Please upload or generate a key first."
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode_message():
    if request.method == 'POST':
        file = request.files['encoded_file']
        encoded_text = file.read().decode('utf-8')
        key_filepath = os.path.join(UPLOAD_FOLDER, 'encryption_key.json')
        if os.path.exists(key_filepath):
            with open(key_filepath, 'r') as file:
                encryption_key = json.load(file)
            decryption_key = {v: k for k, v in encryption_key.items()}
            decoded_text = decode(encoded_text, decryption_key)
            decoded_filename = os.path.join(UPLOAD_FOLDER, 'decoded_message.txt')
            with open(decoded_filename, 'w') as file:
                file.write(decoded_text)
            return send_file(decoded_filename, as_attachment=True)
        else:
            return "Encryption key not found. Please upload or generate a key first."
    return render_template('decode.html')

@app.route('/upload_key_form', methods=['GET'])
def upload_key_form():
    return render_template('upload_key.html')

if __name__ == '__main__':
    app.run(debug=True)
