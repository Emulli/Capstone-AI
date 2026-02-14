import os
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
import datetime

app = Flask(__name__)

# Mock training data: [Hour, Is_Weekend, Rain_Intensity]
X = [[8,0,0], [9,0,0], [18,0,5], [14,1,0], [12,0,8]]
y = [1, 1, 1, 0, 1] # 1=High Risk, 0=Low Risk
model = RandomForestClassifier().fit(X, y)

@app.route('/predict_risk', methods=['GET'])
def predict():
    try:
        hour = datetime.datetime.now().hour
        rain = int(request.args.get('rain', 0))
        prediction = model.predict([[hour, 0, rain]])[0]
        risk = "High" if prediction == 1 else "Low"
        return jsonify({
            "status": "success", 
            "risk_level": risk, 
            "delay_probability": 85 if risk == "High" else 15,
            "suggested_action": "Reroute" if risk == "High" else "Continue"
        })
    except:
        return jsonify({"status": "error", "risk_level": "Normal"})

if __name__ == '__main__':
    # Cloud hosting requires binding to 0.0.0.0 and a dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)