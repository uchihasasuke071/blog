import os
import base64
import json
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# The Secret Key from your BPI Document
SECRET_KEY = b"!PTmluh*EU8#8i5Z"
# We use a file to keep track of polling counts for simulation
POLL_TRACKER = "/tmp/poll_count.txt" if os.name != 'nt' else "poll_count.txt"

def decrypt_data(encrypted_text):
    try:
        raw_data = base64.b64decode(encrypted_text)
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
        decrypted = cipher.decrypt(raw_data)
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except:
        return None

@app.route('/', methods=['POST'])
def pos_service():
    data = request.json
    req_data = data.get("reqData", "")
    decrypted = decrypt_data(req_data)
    
    if not decrypted:
        return jsonify({"respCode": "EN124", "respDesc": "Invalid Encryption"})

    req_json = json.loads(decrypted)
    function = req_json.get("function")

    # CASE 1: Generate QR
    if function == "TP_POS_GENERATE_QR":
        with open(POLL_TRACKER, "w") as f: f.write("0") # Reset poll count
        return jsonify({
            "respCode": "EN00",
            "respDesc": "Success",
            "qrCodeData": "00020101021126480009PH.GCORE.P2P01110000300026331135204581253036085405100005802PH5916EURONET6304"
        })

    # CASE 2: Polling / Inquiry
    elif function == "TP_POS_TXN_ENQ":
        count = 0
        if os.path.exists(POLL_TRACKER):
            with open(POLL_TRACKER, "r") as f: count = int(f.read())
        
        count += 1
        with open(POLL_TRACKER, "w") as f: f.write(str(count))

        if count >= 3: # Succeed on 3rd poll
            return jsonify({"respCode": "EN00", "respDesc": "SUCCESS"})
        else:
            return jsonify({"respCode": "EN01", "respDesc": "PENDING"})

    return jsonify({"respCode": "EN110", "respDesc": "Function Not Found"})

if __name__ == "__main__":
    app.run()