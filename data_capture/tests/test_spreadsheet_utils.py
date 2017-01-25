import copy

from unittest.mock import Mock
from django.test import TestCase
from django.core.exceptions import ValidationError

from ..schedules.spreadsheet_utils import generate_column_index_map


class TestGenerateColumnIndexMap(TestCase):
    def setUp(self):
        self.heading_row = [
            Mock(value='HEADING 2'),
            Mock(value='heading 1'),
            Mock(value='  Heading 3  '),
        ]

        self.field_title_map = {
            'field_1': 'heading 1',
            'field_2': 'heading 2',
            'field_3': 'heading 3',
        }

    def test_generate_column_index_map_works(self):
        col_idx_map = generate_column_index_map(
            self.heading_row, self.field_title_map)
        self.assertEqual(col_idx_map, {
            'field_1': 1,
            'field_2': 0,
            'field_3': 2,
        })

    def test_raises_on_missing_field(self):
        map_with_additional_field = copy.copy(self.field_title_map)
        map_with_additional_field['missing_field'] = 'BOOP'
        with self.assertRaises(ValidationError):
            generate_column_index_map(
                self.heading_row, map_with_additional_field)
