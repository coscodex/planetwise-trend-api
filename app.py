import os
from flask import Flask, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import nltk

# NLTK setup MUST come first
os.environ['NLTK_DATA'] = '/tmp'
nltk.download('stopwords', download_dir='/tmp', quiet=True)

import final1  # Safe to import after NLTK setup

app = Flask(__name__)

# CSV storage directory (project-relative)
CSV_FOLDER = os.path.join(os.path.dirname(__file__), 'csv_files')
os.makedirs(CSV_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Planetwise Trend API is running. Use /run-analyzer and /download-csv."

@app.route('/run-analyzer', methods=['GET'])
def run_analyzer():
    try:
        final1.web_keywords = final1.fetch_web_keywords()
        final1.google_trends_keywords = final1.fetch_google_trends_keywords()
        all_keywords = final1.web_keywords + final1.google_trends_keywords
        top_keywords = final1.get_top_keywords(all_keywords)
        
        file_path = os.path.join(CSV_FOLDER, 'top_keywords.csv')
        final1.save_to_csv(top_keywords, file_path)
        
        return jsonify({"status": "success", "message": "CSV generated"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download-csv')
def download_csv():
    try:
        filename = secure_filename('top_keywords.csv')
        return send_from_directory(CSV_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "CSV not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
