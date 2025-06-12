from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import json
import os
from dotenv import load_dotenv
from waitress import serve
import logging

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
PORT = int(os.getenv("PORT", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
PRE_PROMPT = os.getenv("PRE_PROMPT", "Please answer as concisely as possible: ")
POST_PROMPT = os.getenv("POST_PROMPT", " Thank you.\nRemember to answer in JSON format.")
ENABLE_INPUT_GARD = os.getenv("ENABLE_INPUT_GARD", "true").lower() == "true"
ENABLE_OUTPUT_GARD = os.getenv("ENABLE_OUTPUT_GARD", "true").lower() == "true"
PRINT_USER_PROMPT = os.getenv("PRINT_USER_PROMPT", "true").lower() == "true"
PRINT_WRAPPED_PROMPT = os.getenv("PRINT_WRAPPED_PROMPT", "true").lower() == "true"

# Set up the server configuration
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=LOG_LEVEL)

def wrap_prompt(prompt: str) -> str:
    """Wraps the user prompt with pre-defined pre and post prompts.

    Args:
        prompt (str): The user prompt to be wrapped.

    Returns:
        str: The wrapped prompt with pre and post prompts.
    """

    if PRINT_USER_PROMPT:
        app.logger.info(f"[User Prompt] {prompt}")

    output = f"{PRE_PROMPT}{prompt}{POST_PROMPT}"

    if PRINT_WRAPPED_PROMPT:
        app.logger.info(f"[Wrapped Prompt] {output}")

    return output

# --- Your Guardrail/Preprocessing Logic (from previous answer) ---
def apply_input_guards(prompt_data):
    if not ENABLE_INPUT_GARD:
        return True, ""
    # Example: Simple keyword check
    content = prompt_data.get('prompt') or (prompt_data.get('messages') and prompt_data['messages'][-1]['content'])
    if content and "dangerous_keyword" in content.lower():
        return False, "Input contains a dangerous keyword."
    return True, ""

def apply_output_guards(response_data):
    if not ENABLE_OUTPUT_GARD:
        return True, ""
    # Example: Simple output filtering
    if response_data.get('response') and "sensitive_info" in response_data['response'].lower():
        # You could also redact here instead of blocking
        response_data['response'] = "I cannot provide that information."
    return True, "" # For this example, we always allow (or modified)

@app.before_request
def log_request_info():
    app.logger.info(f"{request.method} {request.path} from {request.remote_addr}")

# --- Ollama API Proxy Endpoints ---

@app.route('/api/generate', methods=['POST'])
def generate_proxy():
    try:
        data = request.json
        model_name = data.get('model')
        prompt_content = data.get('prompt')

        # 1. Apply Input Guards
        is_safe, message = apply_input_guards(data)
        if not is_safe:
            return jsonify({"error": message, "response": ""}), 400 # Bad Request

        # --- Wrap the prompt here ---
        if prompt_content:
            data['prompt'] = wrap_prompt(prompt_content)

        # 2. Forward to Ollama
        ollama_url = f"{OLLAMA_HOST}/api/generate"
        ollama_response = requests.post(ollama_url, json=data, stream=True)
        ollama_response.raise_for_status() # Raise an exception for HTTP errors

        # 3. Apply Output Guards (if needed, and handle streaming)
        # For simplicity, this example processes the *full* response.
        # For true streaming, you'd process chunks.
        full_response_content = ""
        for chunk in ollama_response.iter_content(chunk_size=None): # Or a sensible chunk size
            if chunk:
                try:
                    json_chunk = json.loads(chunk.decode('utf-8'))
                    if 'response' in json_chunk:
                        full_response_content += json_chunk['response']
                except json.JSONDecodeError:
                    # Handle cases where a chunk might not be a complete JSON object
                    pass

        # Reconstruct a similar response structure for output guarding
        guarded_response_data = {'response': full_response_content, 'model': model_name}
        apply_output_guards(guarded_response_data) # This modifies in place

        # 4. Return to the UI
        # If your UI expects a streamed response, you'll need to re-stream it
        # This example sends a single JSON response back, which might break UIs expecting streaming.
        # For true streaming: you'd yield chunks after applying guards.
        return jsonify({"model": model_name, "response": guarded_response_data['response']})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    try:
        data = request.json
        model_name = data.get('model')
        messages = data.get('messages', [])

        # 1. Apply Input Guards (e.g., check the last user message)
        last_user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
        if last_user_message:
            is_safe, message = apply_input_guards({'messages': messages, 'prompt': last_user_message})
            if not is_safe:
                return jsonify({"error": message, "message": {"role": "assistant", "content": "I cannot respond to that due to safety concerns."}}), 400

            # --- Wrap the last user message here ---
            for m in reversed(messages):
                if m['role'] == 'user' and m['content'] == last_user_message:
                    m['content'] = wrap_prompt(last_user_message)
                    break

        # 2. Forward to Ollama and stream response
        ollama_url = f"{OLLAMA_HOST}/api/chat"
        ollama_response = requests.post(ollama_url, json=data, stream=True)
        ollama_response.raise_for_status()

        def generate():
            for chunk in ollama_response.iter_content(chunk_size=None):
                if chunk:
                    try:
                        json_chunk = json.loads(chunk.decode('utf-8'))
                        if 'message' in json_chunk and 'content' in json_chunk['message']:
                            guarded = {'response': json_chunk['message']['content'], 'model': model_name}
                            apply_output_guards(guarded)
                            yield json.dumps({"model": model_name, "message": {"role": "assistant", "content": guarded['response']}}) + "\n"
                    except json.JSONDecodeError:
                        pass

        return Response(stream_with_context(generate()), mimetype='application/json')

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/tags', methods=['GET'])
def tags_proxy():
    try:
        ollama_url = f"{OLLAMA_HOST}/api/tags"
        ollama_response = requests.get(ollama_url)
        ollama_response.raise_for_status()
        return jsonify(ollama_response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {str(e)}"}), 500

@app.route('/api/models', methods=['GET'])
def models_proxy():
    try:
        ollama_url = f"{OLLAMA_HOST}/api/models"
        ollama_response = requests.get(ollama_url)
        ollama_response.raise_for_status()
        return jsonify(ollama_response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {str(e)}"}), 500

# Add other Ollama API endpoints as needed (e.g., /api/show, /api/embeddings)

if __name__ == '__main__':
    # You might want to run this on a different port than Ollama (e.g., 5000)
    # The UI will then connect to this Python server.
    # app.run(host='0.0.0.0', port=PORT, debug=True)
    # serve(app, host='0.0.0.0', port=PORT, threads=4)  # Use Waitress for production
    serve(app, host='0.0.0.0', port=PORT)  # Use Waitress for production
