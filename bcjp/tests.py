import redis
from django.test import TestCase

class RedisTestCase(TestCase):
    def setUp(self):
        self.key = "TEST_CASE_KEY"

    def test_redis_connect(self):
        r = redis.Redis(unix_socket_path='/tmp/redis.sock')
        self.assertIsNone(r.get(self.key))
        r.incrby(self.key, 1)
        self.assertIsNotNone(r.get(self.key))
        r.delete(self.key)
        self.assertIsNone(r.get(self.key))