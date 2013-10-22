from pymongo import MongoClient
from .. import local_config

class ConnectionMixin(object):
    def setUp(self):
        self.client = MongoClient(local_config.host, local_config.port)
        super(ConnectionMixin, self).setUp()
