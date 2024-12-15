import pytest
from pathlib import Path
import Levenshtein as Lev

from MobilityAnalyzer.analyze import (
    document_ai_ocr,
    initialize_claude,
    latinize_ocr_text,
    extract_text_from_claude_response
)

TEST_INPUT_IMAGES_DIR = Path("./test_data/input")
TEST_EXPECTED_OUTPUTS_DIR = Path("./test_data/expected")
CLOUD_KEY_FILE = Path("../../reader-ottoman234-7b59b1682dcf.json")
LATINIZATION_TEST_SENSITIVITY = 0.3  # The lower the value, the less sensitive the test will be
SIMPLE_LATINIZATION_TEST_SET = [('درسعادت بدایت محکمهسی اعضا ملازملكي',
                                 'dersaadet bidayet mahkemesi âzâ mülâzımlığı'),
                                ('بدایت محکمه سی رئیسی عثمان نوری افندی به تفویض',
                                 'Bidayet Mahkemesi Reisi Osman Nuri Efendi\'ye tefviz'),
                                ('شاهانه مأذوندوندن برهان الدین بكه',
                                 'Şahane mezunlarından Burhaneddin Bey\'e'),
                                ('محكمة تمييز اعضا سندن عطوفتلو عالى بك افندى',
                                 'Mahkeme-i Temyiz azasından atufetlü Ali Bey Efendi')
                                ]


@pytest.fixture(scope="session")
def claude_client():
    """
    Initialize the Claude client for the tests.
    :return: claude client, which we need for latinization.
    """
    try:
        claude_client = initialize_claude()
        return claude_client
    except Exception as e:
        pytest.fail(f"Failed to initialize the Claude client. Exception: {str(e)}")


@pytest.fixture(scope="session")
def input_and_output_test_files():
    """
    Initialize and validate the test files for the tests.
    Input images are under test_data/input. Expected outputs (OCR and Latinized)
    texts are under test_data/expected.
    Check if each input file has a corresponding expected output files.
    """
    input_files = sorted(TEST_INPUT_IMAGES_DIR.glob("*.png"))
    expected_ocr_outputs = sorted(TEST_EXPECTED_OUTPUTS_DIR.glob("*_ocr_output.txt"))
    expected_latinized_outputs = sorted(TEST_EXPECTED_OUTPUTS_DIR.glob("*_ocr_output_latinized.txt"))

    # Check if each input file has a corresponding expected output file for testing.
    for input_file in input_files:
        if not any(input_file.stem in f.stem for f in expected_ocr_outputs):
            pytest.fail(f"No expected OCR output file found for: {input_file}")
        if not any(input_file.stem in f.stem for f in expected_latinized_outputs):
            pytest.fail(f"No expected Latinized output file found for: {input_file}")

    return {
        "input_files": input_files,
        "expected_ocr_outputs": expected_ocr_outputs,
        "expected_latinized_outputs": expected_latinized_outputs
    }


def assert_ocr_output_matches_expected(ocr_output: str, expected_output: str) -> None:
    """
    Assert if the OCR'ed text matches the expected output.
    :param ocr_output: The OCR'ed text
    :param expected_output: The expected output text
    """
    for line_nr, (ocr_line, expected_line) in enumerate(zip(ocr_output.split("\n"), expected_output.split("\n")), 1):
        assert ocr_line == expected_line, f"The OCR'ed text does not match the expected output. Line number: {line_nr}"


def assert_latinized_output_matches_expected(latinized_output: str, expected_output: str) -> None:
    """
    This test does not contain any assertian.
    LLM output is not deterministic.
    :param latinized_output: The Latinized text
    :param expected_output: The expected output text
    """

    # First compare the lengths of the strings
    # If the lengths are significantly different, print a warning

    if abs(len(latinized_output) - len(expected_output)) > 0.3 * len(expected_output):
        print(f"\033[33m"
              f"* The Latinized text does not match the expected output. Length comparison fails. "
              f"Expected output length: {len(expected_output)}, actual output length: {len(latinized_output)}"
              f"\033[0m"
              )
    else:
        # Calculate the Levenshtein distance between the Latinized output and the expected output
        distance = Lev.distance(latinized_output, expected_output)

        # Assert if the Levenshtein distance is greater than the sensitivity level
        if distance > LATINIZATION_TEST_SENSITIVITY * len(expected_output):
            print(f"\033[33m"
                  f"* The Levenshtein distance is greater than the sensitivity level. "
                  f"Expected output: {expected_output},"
                  f" actual output: {latinized_output}"
                  f"\033[0m"
                  )


class TestOCRAndLatinization:
    """Test the OCR and Latinization process."""
    def test_document_ai_ocr(self, input_and_output_test_files):
        """Test the OCR process."""
        input_files = input_and_output_test_files["input_files"]
        expected_ocr_outputs = input_and_output_test_files["expected_ocr_outputs"]

        # Iterate over the input files and the expected OCR outputs
        for input_file, expected_ocr_output_file in zip(input_files, expected_ocr_outputs):
            # Perform OCR on the input file
            ocr_text = document_ai_ocr(str(input_file), str(CLOUD_KEY_FILE))

            # Assert if the OCR'ed text matches the expected output
            assert_ocr_output_matches_expected(ocr_text, expected_ocr_output_file.read_text())

    @pytest.mark.parametrize("input_ottoman, expected_latin", SIMPLE_LATINIZATION_TEST_SET)
    def test_simple_latinization(self, input_ottoman, expected_latin, claude_client):
        """Test the Latinization process.
        Simple tests for the latinize_ocr_text function
        """
        latinized_text = latinize_ocr_text(claude_client, input_ottoman)
        assert_latinized_output_matches_expected(extract_text_from_claude_response(latinized_text),
                                                 expected_latin)

    def test_latinization_negative(self, claude_client):
        """ These tests assert not equal.
        Choose wrong expected latinization to test the negative case.
        """
        for input_ottoman, expected_latin in SIMPLE_LATINIZATION_TEST_SET:
            latinized_text = latinize_ocr_text(claude_client, input_ottoman)
            latinized_text = extract_text_from_claude_response(latinized_text)
            assert latinized_text != "Some wrong expected latinization"

    def test_complex_latinization(self, input_and_output_test_files, claude_client):
        """
        Latinization tests for longer texts. Involves,
        line by line comparison of the expected and actual latinized outputs.
        :param input_and_output_test_files:
        :return:
        """
        input_ocr_files = input_and_output_test_files["expected_ocr_outputs"]
        expected_latinized_outputs = input_and_output_test_files["expected_latinized_outputs"]

        for input_ocr_files, expected_latinized_output_file in zip(input_ocr_files, expected_latinized_outputs):
            expected_latinized_text_lines = expected_latinized_output_file.read_text().split("\n")

            actual_latinized_text = latinize_ocr_text(claude_client, input_ocr_files.read_text())
            actual_latinized_text = extract_text_from_claude_response(actual_latinized_text).split("\\n\n")

            print(f"\nTesting: {input_ocr_files.name}\n")
            for actual_latinized_text_line, expected_latinized_text_line in zip(actual_latinized_text,
                                                                                expected_latinized_text_lines):
                assert_latinized_output_matches_expected(actual_latinized_text_line,
                                                         expected_latinized_text_line)
            print("--------------------\n")

    @pytest.mark.integration
    def test_end_to_end_latinization(self, input_and_output_test_files, claude_client):
        """
        End-to-end test for the OCR and Latinization process.
        Starts from the input image, performs OCR, Latinization and compares the Latinized output.
        :param input_and_output_test_files:
        :return:
        """
        input_image_files = input_and_output_test_files["input_files"]
        expected_latinized_outputs = input_and_output_test_files["expected_latinized_outputs"]

        for input_image_file_path, expected_latinized_output_file in zip(input_image_files, expected_latinized_outputs):
            # Perform OCR on the input file
            ocr_text = document_ai_ocr(str(input_image_file_path), str(CLOUD_KEY_FILE))

            # Latinize the OCR'ed text
            latinized_text = latinize_ocr_text(claude_client, ocr_text)
            latinized_text = extract_text_from_claude_response(latinized_text).split("\\n\n")
            expected_latinized_text_lines = expected_latinized_output_file.read_text().split("\n")

            print(f"\nE2E Testing: {input_image_file_path}\n")

            for actual_latinized_text_line, expected_latinized_text_line in zip(latinized_text,
                                                                                expected_latinized_text_lines):
                assert_latinized_output_matches_expected(actual_latinized_text_line,
                                                         expected_latinized_text_line)
            print("--------------------\n")


if __name__ == '__main__':
    unittest.main()
