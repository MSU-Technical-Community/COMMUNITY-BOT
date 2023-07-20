import logging
from threading import Thread
from time import sleep

from datetime import datetime, timedelta

import peewee
from pyparsing import Word, nums

from models import Link, User, UserEvent
from recall import *

#drop_event("Михаил")
add_event("Михаил")