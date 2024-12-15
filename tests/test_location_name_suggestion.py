import pytest
from pathlib import Path
from MobilityAnalyzer.suggest_location import suggest_location
from typing import Dict, List
current_dir = Path(__file__).parent
current_dir / '..' / 'data' / 'ottoman_locations.xlsx'
TEST_LOCATIONS_LIST_FILE = current_dir / '..' / 'data' / 'ottoman_locations.xlsx'

# Locations variations. Format:
# (expected_suggestion, [possible_variation1, possible_variation2, ...])
LOCATION_VARIATIONS = [
    ("istanbul", ['Istanbul', 'Istambul', 'İstanbul', 'İstambul']),
    ("edirne", ['Edirne', 'Edorne', 'Adirne', 'Adorne']),
    ("edirne vilayeti", ['Edirne Vilayeti', 'Edorne Vilayeti', 'Adorne Vilayeti']),
    ("konya", ['Konya', 'Konia', 'Kanya']),
    ("ankara", ['Ankara', 'Angora', 'Ankora']),
    ("ankara vilayeti", ['Ankara Vilayeti', 'Angora Vilayeti', 'Ankora Vilayeti']),
    ("bursa", ['Bursa', 'Burusa', 'Borsa']),
    ("izmir", ['Izmir', 'İzmir']),
    ("meyis", ['Meis', 'miys'])
]


@pytest.fixture(scope="session")
def locations_sheet() -> Path:
    """Fixture for the locations list Excel sheet."""
    if not TEST_LOCATIONS_LIST_FILE.exists():
        pytest.fail(f"Locations list file not found at: {TEST_LOCATIONS_LIST_FILE}")
    return TEST_LOCATIONS_LIST_FILE


class TestLocationNameSuggestion:

    @pytest.mark.parametrize("expected_suggestion, possible_variation", LOCATION_VARIATIONS)
    def test_ottoman_location_name_suggestion(self, locations_sheet: Path, expected_suggestion: str,
                                              possible_variation: List[str]):
        """
        Test the Ottoman location name suggestion system.

        Args:
            expected_suggestion: The expected suggestion.
            possible_variation: The possible variations of the location name.
            locations_sheet: The initialized locations sheet.
        """
        for location_variant in possible_variation:
            suggestions = suggest_location(location_variant, str(locations_sheet))

            assert expected_suggestion in suggestions, \
                f"Expected suggestion '{expected_suggestion}' not found in suggestions: {suggestions}"

    def test_ottoman_location_name_suggestion_empty(self, locations_sheet: Path):
        """Test the Ottoman location name suggestion system with an empty location name."""

        suggestions = suggest_location("", str(locations_sheet))
        assert suggestions[0] == "No suggestion.", "Suggestions should be empty for an empty location name."
        suggestions = suggest_location(None, str(locations_sheet))
        assert suggestions[0] == "No suggestion.", "Suggestions should be empty for an empty location name."

    def test_ottoman_location_name_suggestion_numeric(self, locations_sheet: Path):
        """Test the Ottoman location name suggestion system with an empty location name."""

        suggestions = suggest_location("12358", str(locations_sheet))
        assert suggestions[0] == "No suggestion.", "Suggestions should be empty for an empty location name."
        suggestions = suggest_location("00000", str(locations_sheet))
        assert suggestions[0] == "No suggestion.", "Suggestions should be empty for an empty location name."
        suggestions = suggest_location("99999", str(locations_sheet))
        assert suggestions[0] == "No suggestion.", "Suggestions should be empty for an empty location name."
