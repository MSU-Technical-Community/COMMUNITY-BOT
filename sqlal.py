from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from config import db_name


engine = create_engine(f"sqlite:///{db_name}")


Base = declarative_base()

"""
Basic is basic class for other classes
"""


class Basic(Base):
    id = Column(Integer, primary_key=True)


"""
User is class for user:
where username is username from telegram
group is group of student in university(For example: ПМ_201)
schedule is flag with sending of schedule
verification is flag that show is verified user or not
"""


class User(Basic):
    __tablename__ = "users"
    username = Column(String)
    group = Column(String)
    schedule = Column(Boolean, default=True)
    verification = Column(Boolean, default=False)


"""
Link is table that connects id of user
and key for other tables
"""


class Link(Base):
    user_id = Column(Integer, ForeignKey("users.id"))


"""
It's Basic for tables with events:
name is name of event
place is place for event
description is description of event
time is time of holding of event
"""


class EventBasic(Basic):
    name = Column(String)
    place = Column(String)
    description = Column(String)
    time = Column(DateTime)


"""
UserEvent is table Basicd on EventBasic
that contain link on user
"""


class UserEvet(EventBasic):
    __tablename__ = "user_events"
    user_id = Column(Integer, ForeignKey("Link.id"))


"""
EventUserList contains list of users
subscribed of event
"""


class EventUserList(Basic):
    __tablename__ = "event_members"
    member = Column(Integer, ForeignKey("Link.id"))
    event = Column(Integer, ForeignKey("Event.id"))


"""
Event is table Basicd on EventBasic
that contain link on userlist in
EventUserList
"""


class Event(EventBasic):
    __tablename__ = "events"
    organiser = Column(String)
    requirements = Column(String)


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


class Section(Basic):
    __tablename__ = "sections"
    name = Column(String)
    theme = Column(String)
    manager = Column(String)
    description = Column(String)
    join_info = Column(String)
    contacts = Column(String)


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


class GeoObject(Basic):
    __tablename__ = "places"
    name = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    distance = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)


"""
Cabinet is table witn
informatiom about cabinets:
number is number of cabinet
name is name of cabinet
"""


class Cabinet(Basic):
    __tablename__ = "cabinets"
    number = Column(Integer)
    name = Column(String)
