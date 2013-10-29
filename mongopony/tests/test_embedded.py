from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from ..mapper import SimpleMapper
from .. import fields
from .. import local_config


class Tag(object):
    pass


class TagMapper(SimpleMapper):
    model = Tag

    tag_id = fields.IntField(field_name='i')
    tag_name = fields.StringField(field_name='n')


class Person(object):
    pass


class PeopleMapper(SimpleMapper):
    model = Person

    first_name = fields.StringField(field_name='f')
    last_name = fields.StringField(default='Smith')
    tags = fields.ListField(mapper=TagMapper)


class People(Collection):
    collection_name = 'people'
    document_strategy = PeopleMapper


class TestListFields(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestListFields, self).setUp()
        db_name = local_config.db_prefix + '_db'
        self.client.drop_database(db_name)
        self.db = getattr(self.client, db_name)

    def test_write_person(self):
        person = PeopleMapper.create(
            first_name='Colin', last_name='Howe',
            tags=[TagMapper.create(tag_id=1, tag_name='awesome')])
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Person))
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')
        self.assertTrue(isinstance(person.tags[0], Tag))

    def test_embedded_query(self):
        person = PeopleMapper.create(
            first_name='Colin', last_name='Howe',
            tags=[TagMapper.create(tag_id=1, tag_name='awesome')])
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'tags.tag_id': 1})
        person, = query_plan.as_list()
        self.assertTrue(isinstance(person, Person))
        self.assertEquals(person.first_name, 'Colin')
        self.assertEquals(person.last_name, 'Howe')

    def test_invalid_embedded_query(self):
        person = PeopleMapper.create(
            first_name='Colin', last_name='Howe',
            tags=[TagMapper.create(tag_id=1, tag_name='awesome')])
        People.persist(self.db, person)

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name.tag_id': 1})
        with self.assertRaises(ValueError):
            query_plan.as_list()
