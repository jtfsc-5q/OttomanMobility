import json
import mimetypes
import os
import anthropic
import anthropic.types
import environ
from django.http import JsonResponse
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
from Mobility.settings import BASE_DIR
from MobilityAnalyzer.prompts import LATINIZATION_SYSTEM_PROMPT, STRUCTURED_DATA_EXTRACTION_SYSTEM_PROMPT

env = environ.Env()
try:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except FileNotFoundError:
    raise FileNotFoundError("Please create an .env file in the root directory of the project.")


def initialize_claude():
    """
    Initializes the Claude client.
    Return:
         The Claude client.
    """
    try:
        claude_client_initialized = anthropic.Anthropic(
            api_key=env("CLAUDE_KEY")
        )
        return claude_client_initialized
    except Exception:
        raise Exception("Failed to initialize the Claude client.")


def document_ai_ocr(file_path: str, cloud_key_path: str = env("GOOGLE_CLOUD_KEY_PATH")) -> str:
    """
    Extracts text from an Image/png file using the Document AI API of Google.
    Args:
        cloud_key_path: The path to the Google Cloud API key.
        file_path: The (local) path to the Image file to be OCR'ed.
    Return:
         OCR'ed raw text.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError("The specified file does not exist.")

        # Check if the file is an image with PNG format.
        if not file_path.lower().endswith('.png'):
            raise ValueError("The file should be in PNG format.")

        # Check Mime type
        mime_type = mimetypes.guess_type('image.png')[0]
        if mime_type != 'image/png':
            raise ValueError("The file is not a valid PNG file.")

        with open(file_path, 'rb') as file:
            image_content = file.read()

        gc_client_options = ClientOptions(api_endpoint=f"{env('LOCATION')}-documentai.googleapis.com")
        gc_credentials = service_account.Credentials.from_service_account_file(cloud_key_path)
        gc_client = documentai.DocumentProcessorServiceClient(credentials=gc_credentials,
                                                              client_options=gc_client_options)
        processor_name = f'projects/{env("PROJECT_ID")}/locations/{env("LOCATION")}/processors/{env("PROCESSOR_ID")}'

        raw_image = documentai.RawDocument(content=image_content,
                                           mime_type='image/png')
        request = documentai.ProcessRequest(name=processor_name,
                                            raw_document=raw_image)
        process_result = gc_client.process_document(request=request)

        # Extract the OCR text
        ocred_text = process_result.document.text
        return ocred_text
    except Exception as e:
        raise Exception("Failed to OCR the document using Google Cloud AI: " + str(e))


def latinize_ocr_text(claude_client: anthropic, ottoman_text: str) -> anthropic.types.Message:
    """
    Transliterates OCR'ed Ottoman Turkish text to Latin script using Claude.
    Args:
        ottoman_text: OCR'ed Ottoman Turkish text.
        claude_client: The Claude client.
    Return:
         Latinized text message from Claude.
    """
    try:
        latinized_text = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=3000,
            temperature=0.0,
            system=LATINIZATION_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": "Transliterate this Ottoman Turkish text (may contain OCR errors): " + ottoman_text
                }
            ]
        )

        return latinized_text
    except Exception:
        raise Exception("Failed to Latinize the text using Claude.")


def extract_text_from_claude_response(claude_response: anthropic.types.Message) -> str:
    """
    Extracts the text from the Claude response.
    Args:
        claude_response: The response from Claude.
    Returns:
         The extracted text.
    """
    extracted_text = ""
    # Extract and print the response text
    for content in claude_response.content:
        if content.type == 'text':
            extracted_text += content.text
    return extracted_text


def extract_appointments(claude_client: anthropic, text: str):
    """
    Extracts the OCR'ed and Latinized appointment text and extracts the necessary information.
    Args:
        text: Latinized appointment text.
        claude_client: The Claude client.
    Returns:
         A json output containing the extracted information in the required format.
    """
    try:
        message = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=6000,
            temperature=0.0,
            system=STRUCTURED_DATA_EXTRACTION_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": """Please extract the necessary info and generate JSON from the following text """ + text
                }
            ]
        )
    except Exception:
        raise Exception("Failed to extract the appointment data using Claude.")

    extracted_text = ""
    # Extract and print the response text
    for content in message.content:
        if content.type == 'text':
            extracted_text += content.text

    return extracted_text


def end_to_end_process(file_path) -> JsonResponse:
    """
    Orchestrates the OCR and Latinization process. Entry point.
    Args:
        file_path: The path to the local PDF file to be processed.
    Returns:
         A JSON response containing the OCR'ed and Latinized text.
    """
    try:
        # First OCR the document
        document_ocr_text = document_ai_ocr(file_path)

        try:
            claude_client = initialize_claude()
        except Exception:
            raise Exception("Failed to initialize the Claude client.")

        # Latinize the OCR'ed text
        latinized_claude_response = latinize_ocr_text(claude_client, document_ocr_text)
        latinized_final_text = ""

        # Extract and print the response text
        for content in latinized_claude_response.content:
            if content.type == 'text':
                try:
                    latinized_final_text += content.text
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError("Failed to decode the JSON response from Claude.")

        return JsonResponse({'OCR': document_ocr_text,
                             'Latinized': latinized_final_text}, status=200)
    except Exception as e:
        return JsonResponse({'error': 'Failed to OCR and Latinize the document.' + str(e)}, status=500)
