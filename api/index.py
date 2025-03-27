from http.server import BaseHTTPRequestHandler
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_ed(responses):
    try:
        # Validate fields are booleans (optional)
        required_fields = [
            "stress_anxiety", "anxious_before_sex", "medical_conditions",
            "smoking_alcohol", "weight_fatigue", "medications",
            "pelvic_injury", "pain_curvature", "loud_snoring",
            "autoimmune_conditions", "groin_pain", "tight_grip_masturbation"
        ]
        for field in required_fields:
            if field not in responses or not isinstance(responses[field], bool):
                raise ValueError(f"Field '{field}' must be a boolean (true/false)")

        categories = {
            "Psychological ED": responses["stress_anxiety"] or responses["anxious_before_sex"],
            "Vascular ED": responses["medical_conditions"],
            "Lifestyle-Induced ED": responses["smoking_alcohol"],
            "Hormonal ED": responses["weight_fatigue"],
            "Medication-Induced ED": responses["medications"],
            "Post-Surgical or Injury-Related ED": responses["pelvic_injury"],
            "Peyronie’s Disease": responses["pain_curvature"],
            "Sleep Apnea-Induced ED": responses["loud_snoring"],
            "Autoimmune & Chronic Inflammation-Related ED": responses["autoimmune_conditions"],
            "Pelvic Floor Dysfunction": responses["groin_pain"],
            "Death Grip Syndrome": responses["tight_grip_masturbation"],
        }

        recommendations = {
            "Psychological ED": ["Psychiatrist", "Sexologist"],
            "Vascular ED": ["Andrologist", "Cardiologist"],
            "Lifestyle-Induced ED": ["Andrologist", "Urologist"],
            "Hormonal ED": ["Endocrinologist", "Andrologist"],
            "Medication-Induced ED": ["Andrologist", "Primary Care Doctor"],
            "Post-Surgical or Injury-Related ED": ["Urologist", "Andrologist"],
            "Peyronie’s Disease": ["Urologist", "Andrologist"],
            "Sleep Apnea-Induced ED": ["Sleep Specialist", "Andrologist"],
            "Autoimmune & Chronic Inflammation-Related ED": ["Rheumatologist", "Andrologist"],
            "Pelvic Floor Dysfunction": ["Pelvic Floor Physiotherapist", "Andrologist"],
            "Death Grip Syndrome": ["Sexologist", "Psychosexual Therapist"],
        }

        detected_conditions = [key for key, value in categories.items() if value]
        suggested_doctors = list({doc for condition in detected_conditions for doc in recommendations[condition]})

        return {
            "status": "success",
            "Detected Conditions": detected_conditions,
            "Suggested Doctors": suggested_doctors
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Diagnosis failed: {str(e)}"
        }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            response = {
                "status": "success",
                "message": "Welcome to the ED Diagnosis API! Use POST to send symptoms."
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Empty request body")
            logger.info(f"Received request with content length: {content_length}")
            post_data = self.rfile.read(content_length)
            logger.info(f"Raw POST data: {post_data.decode('utf-8')}")
            data = json.loads(post_data)

            required_fields = [
                "stress_anxiety", "anxious_before_sex", "medical_conditions",
                "smoking_alcohol", "weight_fatigue", "medications",
                "pelvic_injury", "pain_curvature", "loud_snoring",
                "autoimmune_conditions", "groin_pain", "tight_grip_masturbation"
            ]

            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                raise KeyError(f"Missing fields: {', '.join(missing)}")

            result = diagnose_ed(data)
            logger.info(f"Response: {result}")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON format")
        except KeyError as e:
            self.send_error_response(400, f"Validation error: {str(e)}")
        except ValueError as e:
            self.send_error_response(400, f"Bad request: {str(e)}")
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {
            "status": "error",
            "code": code,
            "message": message
        }
        self.wfile.write(json.dumps(error_response).encode('utf-8'))