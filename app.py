from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import werkzeug
import uuid # NEW: Library to generate unique random IDs

# Import your custom functions
from encode_image import encode_image
from decode_image import decode_image 

app = Flask(__name__)
CORS(app)

# Create folders to hold the files
os.makedirs("uploads", exist_ok=True)
os.makedirs("storage", exist_ok=True) # New folder just for secret links

# --- ROUTE 1: CREATE THE SECURE LINK ---
@app.route('/api/generate_link', methods=['POST'])
def api_generate_link():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    secret_text = request.form.get('text', '')
    password = request.form.get('password', '')

    if not file or not secret_text or not password:
        return jsonify({"error": "Missing data"}), 400

    # 1. Save uploaded file temporarily
    filename = werkzeug.utils.secure_filename(file.filename)
    upload_path = os.path.join("uploads", filename)
    file.save(upload_path)

    # 2. Generate a Unique ID for this specific secret
    unique_id = uuid.uuid4().hex
    output_filename = f"{unique_id}.png"
    output_path = os.path.join("storage", output_filename)

    try:
        # 3. Encode and save to our secure storage folder
        encode_image(upload_path, secret_text, password, output_path)
        
        # 4. Clean up the original uploaded file (Good security practice)
        os.remove(upload_path)
        
        # 5. Return the ID so the React frontend can build a link
        return jsonify({"success": True, "id": unique_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- ROUTE 2: OPEN & DESTROY THE SECURE LINK ---
@app.route('/api/open_link', methods=['POST'])
def api_open_link():
    unique_id = request.form.get('id', '')
    password = request.form.get('password', '')

    if not unique_id or not password:
        return jsonify({"error": "Missing ID or password"}), 400

    # 1. Look for the file in the storage folder
    target_path = os.path.join("storage", f"{unique_id}.png")

    # 2. Check if it exists. If not, it was already read (destroyed) or is a fake link!
    if not os.path.exists(target_path):
        return jsonify({"error": "Message not found. It may have already been destroyed!"}), 404

    try:
        # 3. Try to decode it using the provided password
        hidden_message = decode_image(target_path, password)
        
        # 4. SELF-DESTRUCT: If decoding succeeds, delete the file permanently!
        os.remove(target_path)
        
        return jsonify({"secret_message": hidden_message}), 200
    except Exception as e:
        # If the password is wrong, the code jumps here. 
        # Notice we DO NOT delete the file here. We give them another chance to guess.
        return jsonify({"error": str(e)}), 403

# --- ROUTE 3: DISPLAY THE COVER IMAGE ---
@app.route('/api/image/<unique_id>', methods=['GET'])
def api_get_image(unique_id):
    target_path = os.path.join("storage", f"{unique_id}.png")
    
    if os.path.exists(target_path):
        return send_file(target_path, mimetype='image/png')
    else:
        return jsonify({"error": "Image not found or already destroyed"}), 404

if __name__ == '__main__':
    print("Starting Stegano-Share 'View-Once' Server...")
    app.run(debug=True, port=5000)