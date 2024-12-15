import datetime
from django.test import TestCase
from MobilityAnalyzer.models import MovementItem


class MovementItemTestCase(TestCase):
    def setUp(self):
        MovementItem.objects.create(
            name="Person Name1234",
            fromCity="Ankara",
            toCity="Izmir",
            fromTitle="Public Prosecutor",
            toTitle="Judge",
            salary="Not available",
            education="Not available",
            date="1320-06-01",
            source="https://www....",
            notes="Some Notes here!"
        )

    def test_movement_item_str(self):
        movement_item = MovementItem.objects.get(name="Person Name1234")
        self.assertEqual(movement_item.name, "Person Name1234")

    def test_make_sure_date_type(self):
        movement_item = MovementItem.objects.get(name="Person Name1234")
        self.assertIsInstance(movement_item.date, datetime.date,
                              "Date field should be a date object.")
        # Date field should be a string, not a date object.

    def test_default_notes(self):
        empty_notes = MovementItem.objects.create(
            name="Another person1234",
            fromCity="Ankara",
            toCity="Izmir",
            fromTitle="Public Prosecutor",
            toTitle="Judge",
            salary="Not available",
            education="Not available",
            date="1320-06-01",
            source="https://www....",
        )
        # Notes field is not provided.

        self.assertEqual("No notes.", empty_notes.notes,
                         "Notes field should be 'No notes.' by default.")
