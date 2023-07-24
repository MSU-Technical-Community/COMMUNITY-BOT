import os

from peewee import (BooleanField, DateTimeField, FloatField, ForeignKeyField,
                    IntegerField, Model, PrimaryKeyField, SqliteDatabase,
                    TextField, TimeField)

from dotenv import load_dotenv

load_dotenv()
db_name = os.getenv("db_name")

db = SqliteDatabase(db_name)


class Base(Model):
    """
    Base is basic class for other classes
    """
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class User(Base):
    """
    User is class for user:
    where username is username from telegram
    group is group of student in university(For example: ПМ_201)
    schedule is flag with sending of schedule
    verification is flag that show is verified user or not
    """
    telegram_username = TextField()
    group = TextField()
    schedule = BooleanField(default=True)
    verification = BooleanField(default=False)

    class Meta:
        db_table = "users"


class EventBase(Base):
    """
    It's base for tables with events:
    name is name of event
    place is place for event
    description is description of event
    time is time of holding of event
    """
    name = TextField()
    place = TextField()
    description = TextField()
    time = DateTimeField()


class UserEvent(EventBase):
    """
    UserEvent is table based on EventBase
    that contain link on user
    """
    class Meta:
        db_table = "user_events"


class EventUserList(Base):
    """
    EventUserList contains list of users
    subscribed of event
    """
    member = ForeignKeyField(User)

    class Meta:
        db_name = "event_members"


class Event(EventBase):
    """
    Event is table based on EventBase
    that contain link on userlist in
    EventUserList
    """
    organiser = TextField()
    requirements = TextField()
    members = ForeignKeyField(EventUserList)

    class Meta:
        db_table = "official_events"


class Section(Base):
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
    title = TextField()
    theme = TextField()
    manager = TextField()
    description = TextField()
    join_info = TextField()
    contacts = TextField()

    class Meta:
        db_name = "sections"


class GeoObject(Base):
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
    name = TextField()
    latitude = FloatField()
    longitude = FloatField()
    distance = FloatField()
    open_time = TimeField()
    close_time = TimeField()

    class Meta:
        db_name = "places"


class Cabinet(Base):
    """
    Cabinet is table witn
    informatiom about cabinets:
    number is number of cabinet
    name is name of cabinet
    """
    number = IntegerField
    name = TextField()

    class Meta:
        db_table = "cabinets"


class Link(Model):
    """
    Link is table that connects id of user
    and key for other tables
    """
    user_id = ForeignKeyField(User)
    event_id = ForeignKeyField(UserEvent)

    class Meta:
        db_table = "links"
        database = db
