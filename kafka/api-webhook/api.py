from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/delete-file', methods=['POST'])
def delete_file():
    data = request.get_json()  # Get JSON data from the request
    file_path = data.get('file_path')  # Extract the file path
    #/home/ubuntu/largefile.dat
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"File {file_path} deleted successfully"}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
