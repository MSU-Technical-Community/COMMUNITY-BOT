from peewee import (BooleanField, DateTimeField, FloatField, ForeignKeyField,
                    IntegerField, Model, PrimaryKeyField, SqliteDatabase,
                    TextField, TimeField)

from config import db_name

db = SqliteDatabase(db_name)
"""
Base is basic class for other classes
"""


class Base(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


"""
User is class for user:
where username is username from telegram
group is group of student in university(For example: ПМ_201)
schedule is flag with sending of schedule
verification is flag that show is verified user or not
"""


class User(Base):
    username = TextField()
    group = TextField()
    schedule = BooleanField(default=True)
    verification = BooleanField(default=False)

    class Meta:
        db_table = "users"


"""
Link is table that connects id of user
and key for other tables
"""


"""
It's base for tables with events:
name is name of event
place is place for event
description is description of event
time is time of holding of event
"""


class EventBase(Base):
    name = TextField()
    place = TextField()
    description = TextField()
    time = DateTimeField()


"""
UserEvent is table based on EventBase
that contain link on user
"""


class UserEvent(EventBase):
    class Meta:
        db_table = "user_events"


"""
EventUserList contains list of users
subscribed of event
"""


class EventUserList(Base):
    member = ForeignKeyField(User)

    class Meta:
        db_name = "event_members"


class Event(EventBase):
    organiser = TextField()
    requirements = TextField()
    members = ForeignKeyField(EventUserList)

    class Meta:
        db_table = "official_events"


"""
Section is table with information
about section:
name is name of section
theme is theme of section
manager is manager of section
description is description of section
join_info is informatiom for joining
to section
contacts is contacts of manager of
section
"""


class Section(Base):
    name = TextField()
    theme = TextField()
    manager = TextField()
    description = TextField()
    join_info = TextField()
    contacts = TextField()

    class Meta:
        db_name = "sections"


"""
GeoObject is table that
contains information about
this place:
name is name of place
latitude and longitude are
geolocation of place
distance is range between
place and dormitory
time_start and time_end
are time of work of place
"""


class GeoObject(Base):
    name = TextField()
    latitude = FloatField()
    longitude = FloatField()
    distance = FloatField()
    time_start = TimeField()
    time_end = TimeField()

    class Meta:
        db_name = "places"


"""
Cabinet is table witn
informatiom about cabinets:
number is number of cabinet
name is name of cabinet
"""


class Cabinet(Base):
    number = IntegerField
    name = TextField()

    class Meta:
        db_table = "cabinets"


"""
Event is table based on EventBase
that contain link on userlist in
EventUserList
"""


class Link(Model):
    user_id = ForeignKeyField(User)
    event_id = ForeignKeyField(UserEvent)

    class Meta:
        db_table = "links"
        database = db
