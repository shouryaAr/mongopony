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


class PeopleMapper(SimpleMapper):
    model = Person

    first_name = fields.StringField(field_name='f')
    last_name = fields.StringField(default='Smith')


class AthleteMapper(PeopleMapper):
    model = Athlete

    age = fields.IntField()


class ClassFieldMapper(ClassFieldDelegator):
    name_to_mapper = {
        'Athlete': AthleteMapper,
        'Person': PeopleMapper,
    }
    default_mapper = PeopleMapper


class People(Collection):
    collection_name = 'people'
    document_strategy = ClassFieldMapper


class TestPeristence(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestPeristence, self).setUp()
        db_name = local_config.db_prefix + '_db'
        self.client.drop_database(db_name)
        self.db = getattr(self.client, db_name)

    def test_write_person(self):
        person = PeopleMapper.create(first_name='Colin', last_name='Howe')
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Person))
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')

    def test_write_athlete(self):
        person = AthleteMapper.create(
            first_name='Colin', last_name='Howe', age=28)
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Athlete))
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')
        self.assertEquals(person.age, 28)

    def test_update_person_post_create(self):
        person = AthleteMapper.create(
            first_name='Colin', last_name='Howe', age=28)
        People.persist(self.db, person)

        person.age = 29
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertEquals(person.age, 29)

    def test_update_person_post_find(self):
        person = AthleteMapper.create(
            first_name='Colin', last_name='Howe', age=28)
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        person.age = 29
        People.persist(self.db, person)

        person, = query_plan.as_list()
        self.assertEquals(person.age, 29)
