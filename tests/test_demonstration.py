import unittest
from unittest.mock import patch, MagicMock
from weblinx import format_repr, _validate_json_backend, Demonstration

class TestFormatRepr(unittest.TestCase):
    def test_format_repr(self):
        """
        Test the format_repr function to ensure it correctly formats the string
        representation of an object. It checks that the output string matches
        the expected format including class name and attributes.
        """
        class FakeClass:
            def __init__(self):
                self.name = "test_name"
                self.value = 123

        obj = FakeClass()
        result = format_repr(obj, "name", "value")
        self.assertEqual(result, "FakeClass(name=test_name, value=123)")

class TestValidateJsonBackend(unittest.TestCase):
    @patch('importlib.util.find_spec', return_value=MagicMock())
    def test_validate_json_backend_valid(self, mock_find_spec):
        """
        Ensure that the _validate_json_backend function does not raise an error
        when passed a valid backend name. It tests the function with each valid
        backend ('auto', 'json', 'orjson', 'ujson') to confirm proper handling.
        """
        for backend in ["auto", "json", "orjson", "ujson"]:
            _validate_json_backend(backend)  # Should not raise

    @patch('importlib.util.find_spec', return_value=None)
    def test_validate_json_backend_invalid(self, mock_find_spec):
        """
        Tests that the _validate_json_backend function raises a ValueError when
        an invalid backend name is provided. This ensures that the function
        properly validates backend inputs against expected values.
        """
        with self.assertRaises(ValueError):
            _validate_json_backend("invalid_backend")

class TestDemonstration(unittest.TestCase):
    def setUp(self):
        self.demo = Demonstration("aaabtsd", base_dir="./tests/demonstrations")

    def test_repr(self):
        """
        Tests the __repr__ method of the Demonstration class to ensure it
        returns a string representation that accurately reflects the object's
        current state, including its name and base directory.
        """
        self.assertEqual(repr(self.demo), "Demonstration(name=aaabtsd, base_dir=./tests/demonstrations)")

    def test_is_valid(self):
        """
        Verifies that the is_valid method correctly identifies the validity of
        a demonstration by ensuring all required files exist. The test assumes
        all files are present as specified by the mock setup.
        """
        self.assertTrue(self.demo.is_valid())

    @patch('weblinx.Demonstration.load_json', return_value={"version": "1.0.0"})
    def test_get_version(self, mock_load_json):
        """
        Tests the get_version method of the Demonstration class to ensure it
        returns the correct version of the demonstration, both as a tuple and
        as a string, depending on the specified format.
        """
        self.assertEqual(self.demo.get_version(), (1, 0, 0))
        self.assertEqual(self.demo.get_version(as_tuple=False), "1.0.0")

    # Additional tests for methods like load_json, save_json, etc. can be added here.

if __name__ == '__main__':
    unittest.main()
