from django.urls import path
from . import views

urlpatterns = [
    path("", views.ocr, name="index"),
    path("ocr_and_latinize_image", views.ocr_and_latinize_image, name="ocr_and_latinize_image"),
    path("extract_appointment_data", views.extract_appointment_data, name="extract_appointment_data"),
    path("save_appointments", views.save_extracted_appointment_data, name="save_appointments"),
    path("find_location_suggestions", views.find_location_suggestions, name="find_location_suggestions"),
]

