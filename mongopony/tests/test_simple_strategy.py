from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from ..strategy import ClassFieldDelegator, SimpleStrategy
from .. import fields
from .. import local_config


class Person(object):
    pass


class Athlete(Person):
    pass


class SimplePeopleStrategy(SimpleStrategy):
    model = Person

    first_name = fields.StringField()
    last_name = fields.StringField(default='Smith')


class SimpleAthleteStrategy(SimplePeopleStrategy):
    model = Athlete


class ClassFieldStrategy(ClassFieldDelegator):
    name_to_mapper = {
        'Athlete': SimpleAthleteStrategy,
        'Person': SimplePeopleStrategy,
    }
    default_mapper = SimplePeopleStrategy


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

    def test_default(self):
        self.db.people.insert({'first_name': 'Colin'})

        query_plan = People.prepare_query(self.db)
        person, = query_plan.as_list()
        self.assertEquals(person.last_name, 'Smith')

    def test_filter_returns_athletes(self):
        self.db.people.insert({'first_name': 'Colin', '_cls': 'Athlete'})

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Athlete))
        self.assertEquals(person.first_name, 'Colin')


class AliasedPeopleStrategy(SimpleStrategy):
    model = Person

    first_name = fields.StringField(field_name='f')
    last_name = fields.StringField(field_name='l')


class AliasedAthleteStrategy(AliasedPeopleStrategy):
    model = Athlete


class AliasedClassFieldStrategy(ClassFieldDelegator):
    name_to_mapper = {
        'Athlete': AliasedAthleteStrategy,
        'Person': AliasedPeopleStrategy,
    }
    default_mapper = AliasedPeopleStrategy


class Aliased(Collection):
    collection_name = 'aliased'
    document_strategy = AliasedClassFieldStrategy


class TestAliasing(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestAliasing, self).setUp()
        db_name = local_config.db_prefix + '_db'
        self.client.drop_database(db_name)
        self.db = getattr(self.client, db_name)

    def test_document_aliasing(self):
        self.db.aliased.insert({'f': 'Colin', 'l': 'Howe'})
        query_plan = Aliased.prepare_query(self.db)
        person, = query_plan.as_list()
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')

    def test_query_aliasing(self):
        self.db.aliased.insert({'f': 'Colin', 'l': 'Howe'})
        self.db.aliased.insert({'f': 'Chris', 'l': 'Howe'})
        query_plan = Aliased.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')


