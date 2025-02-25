from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://athmardafarin9863:Nottcp5pB5izz@cluster0.arsqy.mongodb.net/?retryWrites=true&w=majority")
db = client["sensor_data"]
collection = db["sensor_readings"]

@app.route("/sensor1/data", methods=["POST"])
def add_sensor_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    temperature = data.get("temperature")
    distance = data.get("distance")

    if temperature is None or distance is None:
        return jsonify({"error": "Missing temperature or distance data"}), 400

    # Format data baru untuk disimpan ke MongoDB
    new_data = {
        "temperature": temperature,
        "distance": distance,
        "timestamp": datetime.datetime.utcnow()
    }

    # Menyimpan data ke MongoDB
    result = collection.insert_one(new_data)

    return jsonify({
        "message": "Data inserted successfully",
        "inserted_id": str(result.inserted_id)
    }), 201

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
