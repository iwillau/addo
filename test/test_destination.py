from logging import basicConfig
from unittest import TestCase
from addo.destination import Destination


class MockSource(object):
    def __init__(self):
        self.metadata = {
            'child_destination': {
                'name': 'Child Destination',
            },
            'parent_destination': {
                'name': 'Parent Destination',
            },
        }


class TestDestinationModel(TestCase):
    def make_destination(self):
        content = {
            'introduction': 'An Introduction',
            'history': {
                'introduction': 'History Introduction',
                'elements': {
                    'near_history': 'Near History',
                    'far_history': 'Far History',
                }
            }
        }
        return Destination(
            source=MockSource(),
            asset_id='1',
            name='super_destination',
            title='Super Destination',
            content=content,
            children=['child_destination'],
            parents=['parent_destination'],
        )

    def test_initialisation(self):
        destination = self.make_destination()
        self.assertEqual(destination.asset_id, '1')
        self.assertEqual(destination.name, 'super_destination')
        self.assertEqual(destination.title, 'Super Destination')

    def test_get_content_one_deep(self):
        destination = self.make_destination()
        self.assertEqual(destination.get_content('introduction'), 'An Introduction')

    def test_get_content_two_deep(self):
        destination = self.make_destination()
        self.assertEqual(destination.get_content('history', 'introduction'), 'History Introduction')

    def test_get_content_dict(self):
        destination = self.make_destination()
        history_elements = destination.get_content('history', 'elements')
        self.assertIsInstance(history_elements, dict)
        self.assertEqual(history_elements['near_history'], 'Near History')

    def test_invalid_content(self):
        destination = self.make_destination()
        self.assertIsNone(destination.get_content('Nothing'))

    def test_invalid_content_one_deep(self):
        destination = self.make_destination()
        self.assertIsNone(destination.get_content('Nothing', 'Else'))

    def test_number_children(self):
        destination = self.make_destination()
        self.assertEqual(destination.number_children(), 1)

    def test_iterate_children(self):
        destination = self.make_destination()
        count = 0
        for child in destination.children():
            count += 1
            self.assertEqual(child['name'], 'Child Destination')
        self.assertEqual(count, 1)

    def test_number_parents(self):
        destination = self.make_destination()
        self.assertEqual(destination.number_parents(), 1)

    def test_iterate_parents(self):
        destination = self.make_destination()
        count = 0
        for parent in destination.parents():
            count += 1
            self.assertEqual(parent['name'], 'Parent Destination')
        self.assertEqual(count, 1)

    def test_invalid_child(self):
        destination = self.make_destination()
        destination._children_list.append('invalid_child')
        count = 0
        for child in destination.children():
            count += 1
            self.assertEqual(child['name'], 'Child Destination')
        self.assertEqual(count, 1)

    def test_invalid_parent(self):
        destination = self.make_destination()
        destination._parent_list.append('invalid_parent')
        count = 0
        for parent in destination.parents():
            count += 1
            self.assertEqual(parent['name'], 'Parent Destination')
        self.assertEqual(count, 1)
