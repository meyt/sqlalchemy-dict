import unittest

from sqlalchemy import Unicode, Integer, Date, Time, Float, ForeignKey, Boolean, DateTime, create_engine
from sqlalchemy.orm import synonym, Session
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_dict import BaseModel, Field, relationship, composite

metadata = MetaData()
DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)


class FullName(object):  # pragma: no cover
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __composite_values__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __repr__(self):
        return "FullName(%s %s)" % (self.first_name, self.last_name)

    def __eq__(self, other):
        return isinstance(other, FullName) and \
               other.first_name == self.first_name and \
               other.last_name == self.last_name

    def __ne__(self, other):
        return not self.__eq__(other)


class Keyword(DeclarativeBase):
    __tablename__ = 'keyword'
    id = Field(Integer, primary_key=True)
    keyword = Field(Unicode(64))


class MemberKeywords(DeclarativeBase):
    __tablename__ = 'member_keywords'
    member_id = Field(Integer, ForeignKey("member.id"), primary_key=True)
    keyword_id = Field(Integer, ForeignKey("keyword.id"), primary_key=True)


class Member(DeclarativeBase):
    __tablename__ = 'member'

    id = Field(Integer, primary_key=True)
    email = Field(Unicode(100), unique=True, index=True)
    title = Field(Unicode(50), index=True)
    first_name = Field(Unicode(50), index=True)
    last_name = Field(Unicode(100), dict_key='lastName')
    is_active = Field(Boolean, nullable=True, readonly=True)
    phone = Field(Unicode(10), nullable=True)
    name = composite(FullName, first_name, last_name, readonly=True, dict_key='fullName')
    _password = Field('password', Unicode(128), index=True, protected=True)
    birth = Field(Date)
    breakfast_time = Field(Time, nullable=True)
    weight = Field(Float(asdecimal=True), default=50)
    _keywords = relationship('Keyword', secondary='member_keywords')
    keywords = association_proxy('_keywords', 'keyword', creator=lambda k: Keyword(keyword=k))
    visible = Field(Boolean, nullable=True)
    last_login_time = Field(DateTime)

    def _set_password(self, password):
        self._password = 'hashed:%s' % password

    def _get_password(self):  # pragma: no cover
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password), info=dict(protected=True))


class BaseModelTestCase(unittest.TestCase):
    member_dict_sample = {
        'title': 'test',
        'firstName': 'test',
        'lastName': 'test',
        'email': 'test@example.com',
        'password': '123456',
        'birth': '2001-01-01',
        'weight': 1.1,
        'visible': 'false'
    }

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session = Session(self.engine)
        DeclarativeBase.metadata.create_all(self.engine)

    def tearDown(self):
        DeclarativeBase.metadata.drop_all(self.engine)

    def test_update_from_dict(self):
        member = Member()
        member.update_from_dict(self.member_dict_sample)

        self.assertEqual(member.title, self.member_dict_sample['title'])
        self.assertEqual(member.password, 'hashed:%s' % self.member_dict_sample['password'])
        self.assertEqual(member.visible, False)
        self.assertEqual(member.weight, 1.1)

    def test_iter_columns(self):
        columns = {c.key: c for c in Member.iter_columns(relationships=False, synonyms=False, composites=False)}
        self.assertEqual(len(columns), 13)
        self.assertNotIn('name', columns)
        self.assertNotIn('password', columns)
        self.assertIn('_password', columns)

    def test_iter_dict_columns(self):
        columns = {c.key: c for c in Member.iter_dict_columns(
            include_readonly_columns=False, include_protected_columns=False)}
        self.assertEqual(len(columns), 12)
        self.assertNotIn('name', columns)
        self.assertNotIn('password', columns)
        self.assertNotIn('_password', columns)

    def test_datetime_format(self):
        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'email': 'test2@example.com',
            'birth': '2001-01-01',
            'lastLoginTime': '2017-10-10T10:10:00.12313'
        })
        member.update_from_dict(member_dict)

        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'email': 'test3@example.com',
            'birth': '2001-01-01',
            'lastLoginTime': '2017-10-10T10:10:00.'
        })
        member.update_from_dict(member_dict)

        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'email': 'test4@example.com',
            'birth': '2001-01-01',
            'lastLoginTime': '2017-10-10T10:10:00'
        })
        member.update_from_dict(member_dict)

        # Invalid month value
        with self.assertRaises(ValueError):
            member = Member()
            member_dict = dict(self.member_dict_sample)
            member_dict.update({
                'lastLoginTime': '2017-13-10T10:10:00'
            })
            member.update_from_dict(member_dict)

        # Invalid datetime format
        with self.assertRaises(ValueError):
            member = Member()
            member_dict = dict(self.member_dict_sample)
            member_dict.update({
                'lastLoginTime': 'InvalidDatetime'
            })
            member.update_from_dict(member_dict)

        # datetime might not have ending Z
        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'lastLoginTime': '2017-10-10T10:10:00.4546'
        })
        member.update_from_dict(member_dict)
        member_result_dict = member.to_dict()
        self.assertEqual(member_result_dict['lastLoginTime'], '2017-10-10T10:10:00')

        # datetime containing ending Z
        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'lastLoginTime': '2017-10-10T10:10:00.4546Z'
        })
        member.update_from_dict(member_dict)
        member_result_dict = member.to_dict()
        self.assertEqual(member_result_dict['lastLoginTime'], '2017-10-10T10:10:00')

    def test_date_format(self):
        # iso date format
        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'birth': '2001-01-01'
        })
        member.update_from_dict(member_dict)
        member_result_dict = member.to_dict()
        self.assertEqual(member_result_dict['birth'], '2001-01-01')

        # none iso date format
        with self.assertRaises(ValueError):
            member = Member()
            member_dict = dict(self.member_dict_sample)
            member_dict.update({
                'birth': '01-01-01'
            })
            member.update_from_dict(member_dict)

        # none iso date format
        with self.assertRaises(ValueError):
            member = Member()
            member_dict = dict(self.member_dict_sample)
            member_dict.update({
                'birth': '2001/01/01'
            })
            member.update_from_dict(member_dict)

    def test_time_format(self):
        # iso time format
        member = Member()
        member_dict = dict(self.member_dict_sample)
        member_dict.update({
            'breakfastTime': '08:08:08',
        })
        member.update_from_dict(member_dict)
        member_result_dict = member.to_dict()
        self.assertEqual(member_result_dict['breakfastTime'], '08:08:08')

        # none iso date format
        with self.assertRaises(ValueError):
            member = Member()
            member_dict = dict(self.member_dict_sample)
            member_dict.update({
                'breakfastTime': '08-08-08'
            })
            member.update_from_dict(member_dict)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
