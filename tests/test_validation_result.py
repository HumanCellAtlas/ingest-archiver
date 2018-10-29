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
        self._do_test_from_json(4, 'Pass', ValidationStatus.PASS)
        self._do_test_from_json(0, ValidationStatus.PENDING)

    def _do_test_from_json(self, version: int, validation_status: ValidationStatus):
        # given:
        json_source = _create_test_json(version=version, status=validation_status.value)

        # when:
        validation_result = ValidationResult.from_json(json_source)

        # then:
        self.assertIsNotNone(validation_result)
        self.assertEqual(version, validation_result.version)
        self.assertEqual(validation_status, validation_result.status)


class ValidationStatusTest(TestCase):

    def test_from_value_unknown(self):
        # expect:
        self.assertEqual(ValidationStatus.UNKNOWN, ValidationStatus.from_value('not in list'))
