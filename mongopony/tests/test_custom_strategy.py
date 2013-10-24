from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from .. import local_config

class CustomPeopleStrategy(object):
    @staticmethod
    def dict_to_object(doc, only_fields):
        return Person(doc['first_name'])

    
    @classmethod
    def get_alias(cls, field_name):
        return field_name

class People(Collection):
    collection_name = 'people'
    document_strategy = CustomPeopleStrategy

class Person(object):
    def __init__(self, first_name):
        self.first_name = first_name

class TestCustomStrategy(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestCustomStrategy, self).setUp()
        db_name = local_config.db_prefix + '_db'
        self.client.drop_database(db_name)
        self.db = getattr(self.client, db_name)

    def test_filter_returns_people(self):
        self.db.people.insert({'first_name': 'Colin'})

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Person))
        self.assertEquals(person.first_name, 'Colin')
