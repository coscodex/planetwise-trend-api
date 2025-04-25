import os
from flask import Flask, jsonify, send_from_directory
import final1  # Your original script that generates the CSV

app = Flask(__name__)

# Directory where the CSV is saved
CSV_FOLDER = 'C:\Users\ashis\Programming\C++\python\Project'  # Update to your desired folder path
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

@app.route('/run-analyzer', methods=['GET'])
def run_analyzer():
    try:
        # Call your original logic to fetch and process keywords
        final1.web_keywords = final1.fetch_web_keywords()
        final1.google_trends_keywords = final1.fetch_google_trends_keywords()
        all_keywords = final1.web_keywords + final1.google_trends_keywords
        top_keywords = final1.get_top_keywords(all_keywords)
        
        # Save the CSV file to the specified folder
        file_path = os.path.join(CSV_FOLDER, 'top_keywords.csv')
        final1.save_to_csv(top_keywords, file_path)

        return jsonify({"status": "success", "message": "Keywords collected and saved."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download-csv', methods=['GET'])
def download_csv():
    try:
        # Send the CSV file for download
        return send_from_directory(CSV_FOLDER, 'top_keywords.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

