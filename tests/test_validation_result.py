from unittest import TestCase

from archiver.usiapi import ValidationResult, ValidationStatus


def _create_test_json(version=0, status='pending'):
    return {
        'version': version,
        'validationStatus': status,
        '_links': {
            'self': {
                'href': 'https://ebi.ac.uk/api/validationResults/88cbdb0'
            }
        }
    }


class ValidationResultTest(TestCase):

    def test_from_json(self):
        self._do_test_from_json(0, 'Pending', ValidationStatus.PENDING)
        self._do_test_from_json(1, 'Pass', ValidationStatus.PASS)
        self._do_test_from_json(1, 'Error', ValidationStatus.ERROR)
        self._do_test_from_json(2, 'Warning', ValidationStatus.WARNING)

    def _do_test_from_json(self, version: int, status: str, validation_status: ValidationStatus):
        # given:
        json_source = _create_test_json(version=version, status=status)

        # when:
        validation_result = ValidationResult.from_json(json_source)

        # then:
        self.assertIsNotNone(validation_result)
        self.assertEqual(version, validation_result.version)
        self.assertEqual(validation_status, validation_result.status)


class ValidationStatusTest(TestCase):

    def test_from_value_case_insensitive(self):
        # expect:
        self._assert_correct_mapping(ValidationStatus.PASS, 'pass', 'Pass', 'paSs', 'PASS')
        self._assert_correct_mapping(ValidationStatus.ERROR, 'error', 'ERROR', 'Error')

    def _assert_correct_mapping(self, expected_status, *variations):
        for variation in variations:
            self.assertEqual(expected_status, ValidationStatus.from_value(variation))

    def test_from_value_unknown(self):
        # expect:
        self.assertEqual(ValidationStatus.UNKNOWN, ValidationStatus.from_value('not in list'))
