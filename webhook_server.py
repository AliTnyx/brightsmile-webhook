#!/usr/bin/env python3
"""
Simple webhook server for BrightSmile Dental appointment management
"""
from flask import Flask, request, jsonify, make_response
import json
from datetime import datetime, timedelta

app = Flask(__name__)

@app.after_request
def after_request(response):
    """Add headers for webhook compatibility"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Content-Type', 'application/json')
    return response

# Mock appointment data
appointments = {
    "john smith": {
        "date": "2025-07-30",
        "time": "3:00 PM",
        "doctor": "Dr. Clark",
        "status": "scheduled"
    },
    "jane doe": {
        "date": "2025-07-29", 
        "time": "10:00 AM",
        "doctor": "Dr. Martinez",
        "status": "scheduled"
    }
}

# Available time slots
available_slots = [
    "2025-07-29 2:00 PM",
    "2025-07-30 10:00 AM", 
    "2025-07-30 4:00 PM",
    "2025-07-31 9:00 AM",
    "2025-07-31 1:00 PM",
    "2025-08-01 11:00 AM"
]

@app.route('/', methods=['GET', 'POST'])
def root():
    """Root endpoint for Telnyx validation"""
    if request.method == 'GET':
        return jsonify({
            "service": "BrightSmile Dental Webhook",
            "status": "online",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return handle_webhook_request()

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    """Main webhook endpoint"""
    if request.method == 'GET':
        return jsonify({
            "service": "BrightSmile Dental Appointment Manager",
            "status": "ready",
            "endpoints": [
                "POST /webhook - Main webhook handler",
                "GET /health - Health check",
                "GET / - Service info"
            ]
        })
    else:
        return handle_webhook_request()

def handle_webhook_request():
    """Handle the actual webhook logic"""
    try:
        data = request.get_json() or {}
        
        # Handle Telnyx validation requests
        if 'type' in data or 'event_type' in data:
            return jsonify({
                "status": "received",
                "message": "Telnyx webhook received successfully"
            })
        
        action = data.get('action', '').lower()
        patient_name = data.get('patient_name', '').lower()
        
        print(f"Received webhook: {json.dumps(data, indent=2)}")
        
        if action == 'lookup_appointment':
            if patient_name in appointments:
                apt = appointments[patient_name]
                return jsonify({
                    "status": "success",
                    "message": f"Found appointment for {patient_name.title()}",
                    "appointment": {
                        "date": apt["date"],
                        "time": apt["time"], 
                        "doctor": apt["doctor"],
                        "status": apt["status"]
                    }
                })
            else:
                return jsonify({
                    "status": "not_found",
                    "message": f"No appointment found for {patient_name.title()}"
                })
        
        elif action == 'check_availability':
            return jsonify({
                "status": "success",
                "available_slots": available_slots[:3],  # Return first 3 slots
                "message": "Here are some available times"
            })
        
        elif action == 'confirm_appointment':
            if patient_name in appointments:
                appointments[patient_name]["status"] = "confirmed"
                return jsonify({
                    "status": "success",
                    "message": f"Appointment confirmed for {patient_name.title()}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Appointment not found"
                })
        
        elif action == 'cancel_appointment':
            if patient_name in appointments:
                appointments[patient_name]["status"] = "cancelled"
                return jsonify({
                    "status": "success", 
                    "message": f"Appointment cancelled for {patient_name.title()}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Appointment not found"
                })
        
        elif action == 'reschedule_appointment':
            new_time = data.get('appointment_time')
            if patient_name in appointments and new_time:
                appointments[patient_name]["date"] = new_time.split()[0]
                appointments[patient_name]["time"] = " ".join(new_time.split()[1:])
                return jsonify({
                    "status": "success",
                    "message": f"Appointment rescheduled for {patient_name.title()} to {new_time}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Could not reschedule appointment"
                })
        
        else:
            return jsonify({
                "status": "error",
                "message": f"Unknown action: {action}"
            })
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("Starting BrightSmile Dental Webhook Server...")
    print("Available endpoints:")
    print("  POST /webhook - Main webhook handler")
    print("  GET /health - Health check")
    app.run(host='0.0.0.0', port=port, debug=False)