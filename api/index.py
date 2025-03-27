from http.server import BaseHTTPRequestHandler
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose_ed(responses):
    try:
        required_fields = [
            "stress_anxiety", "anxious_before_sex", "medical_conditions",
            "smoking_alcohol", "weight_fatigue", "medications",
            "pelvic_injury", "pain_curvature", "loud_snoring",
            "autoimmune_conditions", "groin_pain", "tight_grip_masturbation"
        ]

        # Normalize responses: Convert various forms of Yes/No to boolean
        normalized_responses = {}
        for field in required_fields:
            value = responses[field]
            # Define sets of values for True and False
            true_values = {"yes", "YES", "Yes", "true", True, "True", "true"}
            false_values = {"no", "NO", "No", "null", "false", False, "False", "false", None}

            if value in true_values:
                normalized_responses[field] = True
            elif value in false_values:
                normalized_responses[field] = False
            else:
                raise ValueError(
                    f"Field '{field}' must be a valid boolean-like value (Yes/yes/YES/true or No/no/NO/false/null)")

        categories = {
            "Psychological ED": normalized_responses["stress_anxiety"] or normalized_responses["anxious_before_sex"],
            "Vascular ED": normalized_responses["medical_conditions"],
            "Lifestyle-Induced ED": normalized_responses["smoking_alcohol"],
            "Hormonal ED": normalized_responses["weight_fatigue"],
            "Medication-Induced ED": normalized_responses["medications"],
            "Post-Surgical or Injury-Related ED": normalized_responses["pelvic_injury"],
            "Peyronie’s Disease": normalized_responses["pain_curvature"],
            "Sleep Apnea-Induced ED": normalized_responses["loud_snoring"],
            "Autoimmune & Chronic Inflammation-Related ED": normalized_responses["autoimmune_conditions"],
            "Pelvic Floor Dysfunction": normalized_responses["groin_pain"],
            "Death Grip Syndrome": normalized_responses["tight_grip_masturbation"],
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
            "detected_conditions": detected_conditions,
            "suggested_doctors": suggested_doctors
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
