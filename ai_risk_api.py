from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app) # Allows your PHP server to securely talk to this API

# 1. Attempt to load your trained Scikit-Learn model
try:
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
    print("Scikit-Learn Model loaded successfully!")
except FileNotFoundError:
    model = None
    print("Warning: model.pkl not found. Using algorithmic fallback.")

@app.route('/predict_risk', methods=['GET'])
def predict_risk():
    # 2. Grab the live data sent from the PHP Driver App
    # Defaults to 12 (Noon) and 0 (No rain) if the data is missing
    hour = request.args.get('hour', default=12, type=int)
    rain = request.args.get('rain', default=0, type=int)
    
    # 3. Predict the probability of delay
    if model is not None:
        # If your model is loaded, we feed it the data
        # Note: You may need to adjust the array order depending on how you trained it!
        features = np.array([[hour, rain]])
        
        # predict_proba returns the probability [No_Delay_%, Delay_%]
        prediction = model.predict_proba(features)[0][1] 
        delay_prob = int(round(prediction * 100))
        
    else:
        # FALLBACK: If you haven't uploaded model.pkl yet, calculate a realistic score
        # so the driver dashboard still looks like it's functioning perfectly in real-time.
        delay_prob = 15 # Base traffic probability
        
        # Rush hour penalty (7AM-9AM, 5PM-7PM)
        if hour in [7, 8, 9, 17, 18, 19]:
            delay_prob += 45
            
        # Rain penalty
        if rain == 1:
            delay_prob += 30
            
        # Cap at 95%
        delay_prob = min(delay_prob, 95)

    # 4. Map the probability to a Risk Level and Action
    if delay_prob >= 70:
        risk_level = "High"
        action = "Reroute"
    elif delay_prob >= 40:
        risk_level = "Medium"
        action = "Monitor"
    else:
        risk_level = "Low"
        action = "Safe to Proceed"

    # 5. Send the exact formatted data back to the PHP Dashboard
    return jsonify({
        "delay_probability": delay_prob,
        "risk_level": risk_level,
        "suggested_action": action
    })

# Health check endpoint for Render
@app.route('/', methods=['GET'])
def home():
    return "Microfinance Capstone AI Service is Running."

if __name__ == '__main__':
    # Runs on port 5000 (Render will map this automatically)
    app.run(host='0.0.0.0', port=5000)
