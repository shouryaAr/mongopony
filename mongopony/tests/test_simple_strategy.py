from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from ..strategy import SimpleStrategy
from .. import fields
from .. import local_config


class Person(object):
    pass


class Athlete(object):
    pass


class SimplePeopleStrategy(SimpleStrategy):
    model = Person

    first_name = fields.StringField()


class SimpleAthleteStrategy(SimplePeopleStrategy):
    model = Athlete


class ClassFieldStrategy(object):
    @classmethod
    def dict_to_object(cls, doc):
        if doc.get('_cls') == 'Athlete':
            return SimpleAthleteStrategy.dict_to_object(doc)
        else:
            return SimplePeopleStrategy.dict_to_object(doc)


class People(Collection):
    collection_name = 'people'
    document_strategy = ClassFieldStrategy

class TestSimpleStrategy(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestSimpleStrategy, self).setUp()
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

    def test_filter_returns_athletes(self):
        self.db.people.insert({'first_name': 'Colin', '_cls': 'Athlete'})

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Athlete))
        self.assertEquals(person.first_name, 'Colin')


