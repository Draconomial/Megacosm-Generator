
from megacosm.generators.Flaw import Flaw
from megacosm.generators.Motivation import Motivation
import unittest2 as unittest
from mock import MagicMock

import redis
import ConfigParser, os
from megacosm.util.Seeds import *

from config import TestConfiguration

class TestFlaw(unittest.TestCase):

    def setUp(self):
        """  """
        self.redis=redis.from_url(TestConfiguration.REDIS_URL)
#        self.seed=set_seed( "3" )

    def test_random_flaw(self):
        """  """
        flaw = Flaw(self.redis )
        print flaw.text




