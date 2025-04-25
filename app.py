from flask import Flask, jsonify
import os
import nltk_setup
import final1

app = Flask(__name__)

@app.route('/')
def home():
    return "App is running successfully!"

@app.route('/run-analyzer', methods=['GET'])
def run_analyzer():
    try:
        final1.web_keywords = final1.fetch_web_keywords()
        final1.google_trends_keywords = final1.fetch_google_trends_keywords()
        all_keywords = final1.web_keywords + final1.google_trends_keywords
        top_keywords = final1.get_top_keywords(all_keywords)
        final1.save_to_csv(top_keywords)

        return jsonify({"status": "success", "message": "Keywords collected and saved."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)


