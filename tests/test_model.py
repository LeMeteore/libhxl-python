"""
Unit tests for the hxl.model module
David Megginson
October 2014

License: Public Domain
"""

import unittest
from hxl.model import HXLColumn, HXLRow

class TestColumn(unittest.TestCase):

    HXL_TAG = '#foo'
    LANGUAGE_CODE = 'en'
    HEADER_TEXT = 'Foo header'
    COLUMN_NUMBER = 5
    SOURCE_COLUMN_NUMBER = 7

    def setUp(self):
        self.column = HXLColumn(TestColumn.COLUMN_NUMBER, TestColumn.SOURCE_COLUMN_NUMBER,
                                TestColumn.HXL_TAG, TestColumn.LANGUAGE_CODE, TestColumn.HEADER_TEXT)

    def test_variables(self):
        self.assertEqual(TestColumn.COLUMN_NUMBER, self.column.column_number)
        self.assertEqual(TestColumn.SOURCE_COLUMN_NUMBER, self.column.source_column_number)
        self.assertEqual(TestColumn.HXL_TAG, self.column.tag)
        self.assertEqual(TestColumn.LANGUAGE_CODE, self.column.lang)
        self.assertEqual(TestColumn.HEADER_TEXT, self.column.header)

    def test_display_tag(self):
        self.assertEqual(TestColumn.HXL_TAG + '/' + TestColumn.LANGUAGE_CODE, self.column.displayTag)
        self.column.lang = None
        self.assertEqual(TestColumn.HXL_TAG, self.column.displayTag)

class TestRow(unittest.TestCase):

    ROW_NUMBER = 5
    SOURCE_ROW_NUMBER = 4
    TAGS = ['#sector', '#org', '#country']
    CONTENT = ['Health', 'WFP', 'Liberia'];

    def setUp(self):
        columns = []
        for column_number, tag in enumerate(TestRow.TAGS):
            columns.append(HXLColumn(column_number, -1, tag))
        self.row = HXLRow(columns, TestRow.ROW_NUMBER, TestRow.SOURCE_ROW_NUMBER)
        for content in TestRow.CONTENT:
            self.row.append(content)

    def test_data(self):
        self.assertEqual(TestRow.CONTENT, self.row.values)

    def test_variables(self):
        self.assertEqual(TestRow.ROW_NUMBER, self.row.row_number)
        self.assertEqual(TestRow.SOURCE_ROW_NUMBER, self.row.source_row_number)

    def test_iteration(self):
        expectedLength = len(TestRow.TAGS)
        actualLength = 0;
        for value in self.row:
            actualLength = actualLength + 1
        self.assertEqual(expectedLength, actualLength)

    def test_append(self):
        column_number = len(TestRow.TAGS)
        oldLength = len(self.row.values)
        self.row.append('Lofa County')
        self.assertEqual(oldLength + 1, len(self.row.values))

    def test_get(self):
        self.assertEqual('WFP', self.row.get('#org'))

    def test_getAll(self):
        result = self.row.getAll('#org')
        self.assertTrue(type(result) is list)
        self.assertEqual(1, len(result))

    def test_outofrange(self):
        # what happens when a row is too short?
        self.row.values = self.CONTENT[0:1]
        self.assertEqual(None, self.row.get('#country'))
        self.assertEqual([], self.row.getAll('#country'))

    def test_map(self):

        def tolower(value, column):
            """Function to map over the row"""
            if column.tag == '#org':
                value = value.lower()
            return value

        values = self.row.map(tolower)
        self.assertEqual(['Health', 'wfp', 'Liberia'], values)

# end
