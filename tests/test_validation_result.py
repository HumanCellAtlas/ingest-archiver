from unittest import TestCase

from archiver.usiapi import ValidationResult


class ValidationResultTest(TestCase):

    def test_from_json(self):
        # given:
        json_source = {
            'version': 0,
            'validationStatus': 'valid',
            '_links': {
                'self': {
                    'href': 'https://ebi.ac.uk/api/validationResults/88cbdb0'
                }
            }
        }

        # when:
        validation_result = ValidationResult.from_json(json_source)

        # then:
        self.assertIsNotNone(validation_result)