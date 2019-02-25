import unittest
import json
import config

from archiver import util


class TestUtil(unittest.TestCase):
    def test_is_10x_true(self):
        with open(config.JSON_DIR + 'hca/library_preparation_protocol_10x.json', encoding=config.ENCODING) as data_file:
            lib_prep_protocol = json.loads(data_file.read())

        is10x = util.is_10x(lib_prep_protocol)
        self.assertTrue(is10x)

    def test_is_10x_false(self):
        with open(config.JSON_DIR + 'hca/library_preparation_protocol.json', encoding=config.ENCODING) as data_file:
            lib_prep_protocol = json.loads(data_file.read())

        is10x = util.is_10x(lib_prep_protocol)
        self.assertFalse(is10x)

    def test_flatten_object(self):
        obj = {
            "key1": "a",
            "key2": "b"
        }

        flattened = util.flatten_metadata(obj)
        self.assertEqual(flattened, obj)

    def test_flatten_nested_obj(self):
        obj = {
            "key1": "a",
            "key2": {
                "key3": "b",
                "key4": {
                    "key5": "c"
                }
            }
        }

        expected = {
            "key1": "a",
            "key2__key3": "b",
            "key2__key4__key5": "c"
        }

        flattened = util.flatten_metadata(obj)

        self.assertEqual(expected, flattened)

    def test_flatten_nested_obj_with_list(self):
        obj = {
            "key1": ["a", "b", "c", "d"],
            "key2": {
                "key3": "e",
                "key4": {
                    "key5": "f"
                }
            }
        }

        expected = {
            "key1": "a,b,c,d",
            "key2__key3": "e",
            "key2__key4__key5": "f",
        }

        flattened = util.flatten_metadata(obj)

        self.assertEqual(expected, flattened)
