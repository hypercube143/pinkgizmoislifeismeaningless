import google.generativeai as genai

def prompt(query, model_name, api_key):
    genai.configure(api_key=api_key)

    generation_config = {
        "max_output_tokens": 128,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]

    gemini_ai_model = genai.GenerativeModel(
        model_name=model_name,
        # model_name="gemini-2.0-flash-lite",
        # model_name="gemini-2.5-pro-exp-03-25",
        # model_name="gemini-2.0-flash-thinking-exp",
        # model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    chat_session = gemini_ai_model.start_chat(history=[])

    response = chat_session.send_message(query)
    reply = response.text

    return reply