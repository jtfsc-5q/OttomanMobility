import json
import os
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .analyze import extract_appointments, end_to_end_process, initialize_claude
from .suggest_location import suggest_location
from .models import MovementItem


def ocr(request):
    return render(request, 'ocr.html')


def ocr_and_latinize_image(request) -> JsonResponse:
    """
    OCR and Latinize the uploaded Image file
    Args:
        request: The HTTP request object
    Returns:
        A JSON response containing the OCR'ed and Latinized text
    """
    file_path = None
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'message': 'No file was uploaded'}, status=400)

        file_path = Path('./media') / request.FILES['file'].name
        file_path.parent.mkdir(exist_ok=True)
        file_path.write_bytes(request.FILES['file'].read())
        return end_to_end_process(str(file_path))

    except Exception as e:
        return JsonResponse({'message': f'Failed to OCR and Latinize the document: {e}'}, status=500)

    finally:
        if file_path.exists():
            file_path.unlink()


@require_POST
def save_extracted_appointment_data(request) -> JsonResponse:
    """
    Save the extracted appointment data to the database
    Args:
        request: The HTTP request object
    Returns:
         A JSON response containing the status of the operation
    """
    try:
        body_data = json.loads(request.body)
        if 'appointments' not in body_data:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        if not body_data['appointments']:
            return JsonResponse({'message': 'No appointments was provided.'}, status=400)

        table_data = body_data['appointments']
        appDate = table_data[0]['sourceDate']  # Just pick the first date from the form.
        source = table_data[0]['source']  # Just pick the first source from the form.

        for appointment in table_data:
            MovementItem.objects.create(
                name=appointment['name'],
                fromCity=appointment['fromCity'],
                toCity=appointment['toCity'],
                fromTitle=appointment['fromTitle'],
                toTitle=appointment['toTitle'],
                salary=appointment['salary'],
                education=appointment['education'],
                date=appDate,
                source=source,
                notes=appointment['notes']
            )

        return JsonResponse(
            {'message': 'Extracted data was saved into DB'}, status=200)
    except Exception as e:
        return JsonResponse({'message': f'Saving error: {e}'}, status=400)


@require_POST
def extract_appointment_data(request) -> JsonResponse:
    """
    Extract appointment data from the Latinized text
    Args:
        request: The HTTP request object, containing the Latinized text
    Returns:
         A JSON response containing the extracted appointment data
    """
    try:
        body_data = json.loads(request.body)
        latinized_text = body_data.get('text')

        try:
            claude_client = initialize_claude()
        except Exception:
            raise Exception("Failed to initialize the Claude client.")

        extracted_appointments = json.loads(extract_appointments(claude_client, latinized_text))
        return JsonResponse(extracted_appointments, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)


@require_POST
def find_location_suggestions(request) -> JsonResponse:
    """
    Find location name suggestions for the given text
    using suggest_location function.
    Args:
        request: The HTTP request object, containing the location text
    Returns:
         Array of location suggestions
    """
    try:
        body_data = json.loads(request.body)
        location_text = body_data.get('location_name')
        suggestions = suggest_location(location_text, os.path.join(settings.DATA_DIR,
                                                                   'ottoman_locations.xlsx'))
        return JsonResponse({'suggestions': suggestions}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
