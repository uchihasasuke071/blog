from flask import Flask, request, jsonify
import base64
from Crypto.Cipher import AES

app = Flask(__name__)

# This matches the key in your BPI documentation
SECRET_KEY = b"!PTmluh*EU8#8i5Z"

def decrypt_data(encrypted_text):
    try:
        raw_data = base64.b64decode(encrypted_text)
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
        decrypted = cipher.decrypt(raw_data)
        # PKCS5 padding removal
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except Exception as e:
        return f"Decryption Error: {str(e)}"

@app.route('/third-party/pos/service/', methods=['POST'])
def pos_service():
    print("\n--- Incoming Request from Sunmi ---")
    data = request.json
    req_data = data.get("reqData", "")
    
    if req_data:
        decrypted = decrypt_data(req_data)
        print(f"Decrypted Data: {decrypted}")
    
    # Returning the standard Euronet Success Response
    return jsonify({
        "respCode": "EN00",
        "respDesc": "Success",
        "qrCodeData": "00020101021126480009PH.GCORE.P2P01110000300026331135204581253036085405100005802PH5916EURONET6304"
    })

if __name__ == '__main__':
    print("Mock Server is running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
