from google.genai import Client

def generate_ai_response(prompt):
    client = Client(api_key="AIzaSyCBqDLJaIcPjbyoHyb2FfXxeX99Mmq_XSE")
    model_id = "gemini-1.5-flash-002"  # Specify the model you're using
    contents = [prompt]

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=contents
        )
        # Extract the generated text from the response
        generated_text = response.candidates[0].content.parts[0].text
        
        # Clean up the response to remove unwanted formatting
        cleaned_text = generated_text.replace('**', '').replace('*', '')
        
        return cleaned_text
    except Exception as e:
        return f"An error occurred while generating the response: {e}"
