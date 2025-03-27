from http.server import BaseHTTPRequestHandler
import json


def diagnose_ed(responses):
    try:
        categories = {
            "Psychological ED": responses.get("stress_anxiety", False) or responses.get("anxious_before_sex", False),
            "Vascular ED": responses.get("medical_conditions", False),
            "Lifestyle-Induced ED": responses.get("smoking_alcohol", False),
            "Hormonal ED": responses.get("weight_fatigue", False),
            "Medication-Induced ED": responses.get("medications", False),
            "Post-Surgical or Injury-Related ED": responses.get("pelvic_injury", False),
            "Peyronie’s Disease": responses.get("pain_curvature", False),
            "Sleep Apnea-Induced ED": responses.get("loud_snoring", False),
            "Autoimmune & Chronic Inflammation-Related ED": responses.get("autoimmune_conditions", False),
            "Pelvic Floor Dysfunction": responses.get("groin_pain", False),
            "Death Grip Syndrome": responses.get("tight_grip_masturbation", False),
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
    def do_GET(self):
        try:
            response = {
                "status": "success",
                "message": "Welcome to the ED Diagnosis API! Use POST to send symptoms."
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        try:
            # Validate content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Empty request body")
            print(content_length)
            # Read and parse JSON
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            # Validate required fields
            required_fields = [
                "stress_anxiety", "anxious_before_sex", "medical_conditions",
                "smoking_alcohol", "weight_fatigue", "medications",
                "pelvic_injury", "pain_curvature", "loud_snoring",
                "autoimmune_conditions", "groin_pain", "tight_grip_masturbation"
            ]

            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                raise KeyError(f"Missing fields: {', '.join(missing)}")

            # Process request
            result = diagnose_ed(data)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
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
        self.end_headers()
        error_response = {
            "status": "error",
            "code": code,
            "message": message
        }
        self.wfile.write(json.dumps(error_response).encode('utf-8'))