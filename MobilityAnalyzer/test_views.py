import json
from pathlib import Path

from django.test import TestCase
from django.urls import reverse


class ViewTestCase(TestCase):

    def setUp(self):
        self.appointment_data = {
            "appointments": [
                {
                    "name": "New Name1234",
                    "fromCity": "Erzurum",
                    "toCity": "Izmir",
                    "fromTitle": "Public Prosecutor",
                    "toTitle": "Public Prosecutor",
                    "salary": "Not available",
                    "education": "Not available",
                    "sourceDate": "1310-06-01",
                    "source": "https://www....",
                    "notes": "Some Notes here!"
                },
                {
                    "name": "Best Name1234",
                    "fromCity": "Samsun",
                    "toCity": "Mersin",
                    "fromTitle": "Judge",
                    "toTitle": "Judge",
                    "salary": "Not available",
                    "education": "Not available",
                    "sourceDate": "1320-06-01",
                    "source": "https://www....",
                    "notes": "My notes"
                }
            ]
        }

        self.text_to_extract_appointments = {
            "text": """Akçehisar kazâsı bidâyet mahkemesi riyâseti mekteb-i
                    hukuk-ı şâhâne me'zûnlarından Mehmed Emin Efendi'ye
                    kazâ-yı mezbûr müddeî-i umûmî muâvinliği Manastır
                    vilâyeti merkez bidâyet mahkemesi ikinci müstantıkı Fâik
                    Efendi'ye
                    Şiyak kazâsı bidâyet mahkemesi riyâseti Trablus-ı Garb
                    vilâyeti merkez bidâyet mahkemesi ikinci müstantıkı Dâvud
                    Efendi'ye
                    kazâ-yı mezbûr müddeî-i umûmî muâvinliği Ertuğrul
                    sancağı bidâyet mahkemesi icrâ me'mûru Nâzım Efendi'ye
                    Tiran kazâsı bidâyet mahkemesi riyâseti Bingazi
                    sancağı bidâyet mahkemesi müstantıkı Ali Rıza Efendi'ye
                    kazâ-yı mezbûr müddeî-i umûmî muâvinliği Seydişehir
                    sancağı bidâyet mahkemesi müstantıkı Tevfik Bey'e"""
        }

        self.location_suggestions_test = [
            {"location_name": "Istambol"},
            {"location_name": "Istambul"},
            {"location_name": "Angora"},
        ]

    def test_ocr_and_latinize_image(self):
        current_dir = Path(__file__).parent
        test_image_path = current_dir / '..' / 'tests' / 'test_data' / 'input' / 'ottoman_test1.png'
        with open(test_image_path, 'rb') as f:
            response = self.client.post(reverse('ocr_and_latinize_image'),
                                        {'file': f})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['OCR']) > 0)
        self.assertTrue(len(response.json()['Latinized']) > 0)

    def test_save_extracted_appointment_data(self):
        test_data = self.appointment_data
        response = self.client.post(reverse('save_appointments'),
                                    json.dumps(test_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Extracted data was saved into DB')

    def test_extract_appointment_data(self):
        test_data = self.text_to_extract_appointments
        response = self.client.post(reverse('extract_appointment_data'),
                                    json.dumps(test_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        for appointment in response.json()['appointments']:
            self.assertTrue("name" in appointment)
            self.assertTrue("fromCity" in appointment)
            self.assertTrue("toCity" in appointment)
            self.assertTrue("fromTitle" in appointment)
            self.assertTrue("toTitle" in appointment)
            self.assertTrue("salary" in appointment)

    def test_find_location_suggestions(self):
        test_data = self.location_suggestions_test
        for location in test_data:
            response = self.client.post(reverse('find_location_suggestions'),
                                        json.dumps(location),
                                        content_type='application/json')

            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.json()) > 0)


