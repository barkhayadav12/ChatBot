from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from googletrans import Translator

app = Flask(__name__)

# Configure Gemini API Key
genai.configure(api_key="your_gemini_api_key") 

# Initialize Google Gemini Model
model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize Google Translator
translator = Translator()

# List of agriculture-related keywords
agriculture_keywords = [
    # General Farming
    "farming", "agriculture", "farmer", "farmers", "harvest", "irrigation", "cultivation",
    "crop", "crops", "seeds", "yield", "agri", "agronomy", "rural", "organic farming",
    "modern farming", "vertical farming", "mixed farming", "hydroponics", "aeroponics",
    "drip irrigation", "flood irrigation", "crop rotation", "intercropping", "cover crops",
    "monoculture", "polyculture",

    # Soil Types
    "soil", "black soil", "clay soil", "sandy soil", "loamy soil", "red soil", "saline soil",
    "alkaline soil", "soil erosion", "soil fertility", "soil health", "soil pH", "soil testing",

    # Fertilizers & Pesticides
    "fertilizer", "pesticide", "organic fertilizer", "chemical fertilizer", "compost",
    "urea", "DAP", "potash", "NPK", "nitrogen", "phosphorus", "potassium", "bio-fertilizer",
    "vermicompost", "manure", "cow dung", "mulching", "top dressing", "side dressing",

    # Plant Diseases
    "plant disease", "fungal infection", "viral disease", "bacterial disease",
    "early blight", "late blight", "mosaic virus", "rust", "wilt", "powdery mildew",
    "leaf spot", "root rot", "blossom end rot", "plant health", "disease control",

    # Fruits and Vegetables
    "tomato", "potato", "wheat", "rice", "maize", "corn", "sugarcane", "mustard", "cotton",
    "guava", "papaya", "banana", "mango", "citrus", "apple", "grapes", "pomegranate",
    "onion", "garlic", "cabbage", "cauliflower", "brinjal", "spinach", "okra", "ladyfinger",

    # Livestock & Animal Farming
    "dairy", "poultry", "goat farming", "fish farming", "livestock", "animal husbandry",
    "chicken", "eggs", "milk production", "cattle", "cow", "buffalo", "duck farming",
    "fish feed", "cattle feed", "vaccination", "fodder", "silage", "cattle farm",

    # Farming Techniques
    "zero tillage", "minimum tillage", "no-till farming", "precision farming", "agroforestry",
    "crop diversification", "integrated farming", "controlled environment farming",
    "organic farming", "greenhouse farming", "protected cultivation", "shade net farming",

    # Government Schemes
    "PM Kisan", "crop insurance", "Kisan Credit Card", "PMFBY", "PM Kisan Samman Nidhi",
    "Fasal Bima Yojana", "subsidy", "loan", "minimum support price", "MSP", "agriculture loan",
    "farmer welfare", "agriculture policy", "Krishi Vigyan Kendra", "KVK",

    # Market & Yield
    "crop yield", "market price", "wholesale market", "mandi", "market rate",
    "commodity rate", "export", "import", "cold storage", "storage facility", "warehousing",

    # Modern Technologies
    "drones in agriculture", "AI in farming", "satellite imaging", "weather forecast",
    "remote sensing", "precision agriculture", "smart farming", "IoT in agriculture",
    "AI chatbot", "robotic farming", "automated irrigation", "soil sensor",

    # Weather Impact
    "climate change", "weather conditions", "drought", "flood", "monsoon", "rainfall",
    "humidity", "temperature", "frost", "hailstorm", "storm", "natural disaster",

    # Miscellaneous
    "tractor", "combine harvester", "farm machinery", "irrigation pump", "solar pump",
    "kisan helpline", "krishi vigyan", "agriculture technology", "seed quality"
]


@app.route('/')
def index():
    return render_template('index.html')


def detect_language(text):
    """
    Detect the language of the user's input text.
    """
    detection = translator.detect(text)
    detected_lang = detection.lang
    return detected_lang


def get_answer_google_ai(question):
    """
    Generate an AI response in English using Gemini AI
    ONLY if the question is agriculture-related.
    """
    # Check if the question contains any agriculture keyword
    if any(word in question.lower() for word in agriculture_keywords):
        #  Generate the response from Gemini AI
        response = model.generate_content(question)
        formatted_response = format_response(response.text)
        return formatted_response
    else:
        #  Reject non-agriculture questions
        return "🚫 I am designed to answer **Agriculture-related questions only.** 🌱"


def format_response(response_text):
    """
    Add beautiful emojis to the response for better understanding.
    """
    lines = response_text.split('\n')
    formatted_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        #  Add custom emojis based on keywords
        if "farming" in line.lower():
            formatted_text += f'🚜 **Farming:** {line}\n\n'
        elif "soil" in line.lower():
            formatted_text += f'🪴 **Soil:** {line}\n\n'
        elif "fertilizer" in line.lower():
            formatted_text += f'💊 **Fertilizer:** {line}\n\n'
        elif "pesticide" in line.lower():
            formatted_text += f'🦟 **Pesticide:** {line}\n\n'
        elif "weather" in line.lower():
            formatted_text += f'⛅ **Weather:** {line}\n\n'
        elif "disease" in line.lower():
            formatted_text += f'🦠 **Plant Disease:** {line}\n\n'
        else:
            formatted_text += f'👉 {line}\n\n'

    return formatted_text


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle user input and AI response.
    """
    text = request.form.get("text")
    if not text:
        return jsonify({"text": "❌ Invalid request."})

    #  Step 1: Detect the user's language
    detected_lang = detect_language(text)

    #  Step 2: Translate the question to English
    if detected_lang != 'en':
        translated_text = translator.translate(text, src=detected_lang, dest='en').text
    else:
        translated_text = text

    #  Step 3: Generate AI response in English
    ai_response = get_answer_google_ai(translated_text)

    #  Step 4: Translate the response back to the user's language
    if detected_lang != 'en':
        final_response = translator.translate(ai_response, src='en', dest=detected_lang).text
    else:
        final_response = ai_response

    #  Step 5: Return the final response
    return jsonify({"text": final_response})


if __name__ == "__main__":
    app.run(debug=True)
