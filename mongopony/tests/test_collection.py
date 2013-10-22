from .base import ConnectionMixin
from unittest import TestCase
from ..collection import Collection
from .. import local_config

class People(Collection):
    collection_name = 'people'

class TestCollection(ConnectionMixin, TestCase):
    def setUp(self):
        super(TestCollection, self).setUp()
        db_name = local_config.db_prefix + '_db'
        self.client.drop_database(db_name)
        self.db = getattr(self.client, db_name)

    def test_unfiltered_count(self):
        self.db.people.insert({'first_name': 'Colin'})

        query_plan = People.prepare_query(self.db)
        self.assertEquals(1, query_plan.count())

    def test_filtered_count(self):
        self.db.people.insert({'first_name': 'Colin'})

        query_plan = People.prepare_query(self.db)
        query_plan.filter({'first_name': 'Colin'})
        self.assertEquals(1, query_plan.count())

        query_plan.filter({'first_name': 'Bob'})
        self.assertEquals(0, query_plan.count())
