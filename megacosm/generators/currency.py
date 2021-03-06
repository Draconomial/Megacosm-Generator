#!/usr/bin/env python
# -*- coding: utf-8 -*-

from generator import Generator
from npc import NPC
import logging
import random


class Currency(Generator):

    """ Define a currency to be used in your game """

    def __init__(self, redis, features={}):

        Generator.__init__(self, redis, features)
        self.logger = logging.getLogger(__name__)

        if not hasattr(self, 'count'):
            self.count = random.randint(self.amount['min'], self.amount['max'])

        # Perhaps your currency has a person on it- a king, queen, etc.

        if not hasattr(self, 'npc'):
            setattr(self, 'npc', NPC(self.redis))
        self.logger.error('test')

        # Double parse the template to fill in templated template values.

        if not hasattr(self, 'text'):
            self.text = self.render_template(self.template)
            self.text = self.render_template(self.text)
        self.text = self.text[0].capitalize() + self.text[1:]

    def __str__(self):
        return self.text
