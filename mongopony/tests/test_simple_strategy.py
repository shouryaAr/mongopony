from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from ..mapper import ClassFieldDelegator, SimpleMapper
from .. import fields
from .. import local_config


class Person(object):
    pass


class Athlete(Person):
    pass


class SimplePeopleMapper(SimpleMapper):
    model = Person

    first_name = fields.StringField()
    last_name = fields.StringField(default='Smith')


class SimpleAthleteMapper(SimplePeopleMapper):
    model = Athlete


class ClassFieldMapper(ClassFieldDelegator):
    name_to_mapper = {
        'Athlete': SimpleAthleteMapper,
        'Person': SimplePeopleMapper,
    }
    default_mapper = SimplePeopleMapper


class People(Collection):
    collection_name = 'people'
    document_strategy = ClassFieldMapper


class TestSimpleMapper(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestSimpleMapper, self).setUp()
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

    def test_subset_of_fields(self):
        self.db.people.insert({'first_name': 'Colin'})

        query_plan = People.prepare_query(self.db)
        query_plan.only('first_name')
        person, = query_plan.as_list()
        self.assertFalse(hasattr(person, 'last_name'))


class AliasedPeopleMapper(SimpleMapper):
    model = Person

    first_name = fields.StringField(field_name='f')
    last_name = fields.StringField(field_name='l')


class AliasedAthleteMapper(AliasedPeopleMapper):
    model = Athlete


class AliasedClassFieldMapper(ClassFieldDelegator):
    name_to_mapper = {
        'Athlete': AliasedAthleteMapper,
        'Person': AliasedPeopleMapper,
    }
    default_mapper = AliasedPeopleMapper


class Aliased(Collection):
    collection_name = 'aliased'
    document_strategy = AliasedClassFieldMapper


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


