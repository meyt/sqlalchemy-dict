import json
import pytest

from sqlalchemy import (
    UnicodeText,
    Unicode,
    DateTime,
    Date,
    Time,
    Integer,
    Float,
    ForeignKey,
    Boolean,
    create_engine,
    Enum,
    TypeDecorator,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_dict import BaseModel, Field, relationship, composite, synonym

metadata = MetaData()
DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)


class JsonType(TypeDecorator):  # pragma: no cover
    impl = UnicodeText

    def process_bind_param(self, value, engine):
        return json.dumps(value)

    def process_result_value(self, value, engine):
        if value is None:
            return None

        return json.loads(value)

    @property
    def python_type(self):
        return dict


class MyType(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        return "PREFIX:" + value

    def process_result_value(self, value, dialect):
        return value[7:]


class FullName(object):  # pragma: no cover
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __composite_values__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __repr__(self):
        return "FullName(%s %s)" % (self.first_name, self.last_name)

    def __eq__(self, other):
        return (
            isinstance(other, FullName)
            and other.first_name == self.first_name
            and other.last_name == self.last_name
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class Keyword(DeclarativeBase):
    __tablename__ = "keyword"
    id = Field(Integer, primary_key=True)
    keyword = Field(Unicode(64))


class MemberKeywords(DeclarativeBase):
    __tablename__ = "member_keywords"
    member_id = Field(Integer, ForeignKey("member.id"), primary_key=True)
    keyword_id = Field(Integer, ForeignKey("keyword.id"), primary_key=True)


class Member(DeclarativeBase):
    __tablename__ = "member"

    id = Field(Integer, primary_key=True)
    email = Field(Unicode(100), unique=True, index=True)
    title = Field(Unicode(50), index=True)
    first_name = Field(Unicode(50), index=True)
    last_name = Field(Unicode(100), dict_key="lastName")
    is_active = Field(Boolean, nullable=True, readonly=True)
    phone = Field(Unicode(10), nullable=True)
    name = composite(
        FullName, first_name, last_name, readonly=True, dict_key="fullName"
    )
    name_alternative = composite(
        FullName, first_name, last_name, protected=True
    )
    _password = Field("password", Unicode(128), index=True, protected=True)
    birth = Field(Date)
    breakfast_time = Field(Time, nullable=True)
    weight = Field(Float(asdecimal=True), default=50)
    _keywords = relationship(
        "Keyword",
        secondary="member_keywords",
        dict_key="keywords",
        protected=True,
    )
    _keywords_not_protected = relationship(
        "Keyword", secondary="member_keywords"
    )
    keywords = association_proxy(
        "_keywords", "keyword", creator=lambda k: Keyword(keyword=k)
    )
    visible = Field(Boolean, nullable=True)
    last_login_time = Field(DateTime)
    role = Field(Enum("admin", "manager", "normal", name="member_role_name"))
    meta = Field(JsonType)
    assigner_id = Field(Integer, ForeignKey("member.id"), nullable=True)
    assigner = relationship("Member", uselist=False)
    my_type = Field(MyType, default="init")
    _avatar = Field("avatar", Unicode(255), nullable=True, protected=True)
    _cover = Field("cover", Unicode(255), nullable=True, protected=True)

    def _set_password(self, password):
        self._password = "hashed:%s" % password

    def _get_password(self):  # pragma: no cover
        return self._password

    password = synonym(
        "_password",
        descriptor=property(_get_password, _set_password),
        protected=True,
    )

    def _set_avatar(self, avatar):  # pragma: no cover
        self._avatar = "avatar:%s" % avatar

    def _get_avatar(self):  # pragma: no cover
        return self._avatar

    avatar = synonym(
        "_avatar",
        descriptor=property(_get_avatar, _set_avatar),
        protected=False,
    )

    def _set_cover(self, cover):  # pragma: no cover
        self._cover = "cover:%s" % cover

    def _get_cover(self):  # pragma: no cover
        return self._cover

    cover = synonym(
        "_cover",
        descriptor=property(_get_cover, _set_cover),
        dict_key="coverImage",
        readonly=True,
    )

    @hybrid_property
    def is_visible(self):
        return self.visible

    @is_visible.setter
    def is_visible(self, value):
        self.visible = value

    @is_visible.expression
    def is_visible(self):
        return self.visible.is_(True)


member_dict_sample = {
    "title": "test",
    "firstName": "test",
    "lastName": "test",
    "email": "test@example.com",
    "password": "123456",
    "birth": "2001-01-01",
    "weight": 1.1,
    "visible": "false",
    "isVisible": False,
    "lastLoginTime": "2017-10-10T10:10:00.12313",
    "role": "admin",
    "myType": "test",
    "meta": {"score": 5, "language": "english"},
}


class DatabaseWrapper(object):
    db_url = "sqlite:///:memory:"

    def __init__(self):
        self.engine = create_engine(self.db_url)
        self.session = Session(self.engine)

    def __enter__(self):
        DeclarativeBase.metadata.drop_all(self.engine)
        DeclarativeBase.metadata.create_all(self.engine)
        return self

    def __exit__(self, *args):
        self.session.close()
        self.session.get_bind().dispose()


@pytest.fixture(scope="function", autouse=True)
def db():
    with DatabaseWrapper() as wrapper:
        yield wrapper


def test_update_from_dict(db):
    member = Member()
    member.update_from_dict(member_dict_sample)

    assert member.title == member_dict_sample["title"]
    assert member.password == "hashed:%s" % member_dict_sample["password"]
    assert member.visible is False
    assert member.weight == 1.1
    assert member.meta == member_dict_sample["meta"]
    db.session.add(member)

    @Member.expose
    def testing_expose(title=None):
        query = db.session.query(Member)
        if title:
            return query.filter_by(title=title).one_or_none()
        return query

    # Query output
    result = testing_expose()
    assert result[0]["title"] == member_dict_sample["title"]

    # One object output
    result = testing_expose(title=member_dict_sample["title"])
    assert result["title"] == member_dict_sample["title"]

    # None
    result = testing_expose(title="What?")
    assert result is None

    # Boolean value
    member.update_from_dict(dict(visible=True))
    assert member.visible is True

    member.update_from_dict(dict(visible=False))
    assert member.visible is False

    member.update_from_dict(dict(visible=None))
    assert member.visible is None


def test_get_column():
    title_column = Member.get_column("title")
    assert isinstance(title_column, Field)


def test_relationship(db):
    assigner = Member()
    assigner.update_from_dict(member_dict_sample)
    assigner.email = "test2@example.com"

    member = Member()
    member.keywords.append("keyword_one")
    member.assigner = assigner
    member.update_from_dict(member_dict_sample)
    db.session.add(member)
    db.session.commit()
    result_dict = member.to_dict()
    assert len(result_dict["KeywordsNotProtected"]) == 1

    db.session.query(Member).delete()
    db.session.commit()


def test_iter_columns():
    columns = {
        c.key: c
        for c in Member.iter_columns(
            relationships=False, synonyms=False, composites=False
        )
    }
    assert len(columns) == 20
    assert "name" not in columns
    assert "password" not in columns
    assert "_password" in columns

    columns = {
        c.key: c
        for c in Member.iter_columns(
            relationships=False,
            synonyms=False,
            composites=False,
            use_inspection=False,
        )
    }
    assert len(columns) == 19
    assert "is_visible" not in columns
    assert "_password" not in columns
    assert "password" in columns


def test_iter_dict_columns():
    columns = {
        c.key: c
        for c in Member.iter_dict_columns(
            include_readonly_columns=False, include_protected_columns=False
        )
    }
    assert len(columns) == 19
    assert "name" not in columns
    assert "password" not in columns
    assert "_password" not in columns
    assert "_avatar" not in columns
    assert "coverImage" not in columns
    assert "avatar" in columns


def test_datetime_format():
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00."})
    member.update_from_dict(member_dict)

    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00"})
    member.update_from_dict(member_dict)

    # Invalid month value
    with pytest.raises(ValueError):
        member = Member()
        member_dict = dict(member_dict_sample)
        member_dict.update({"lastLoginTime": "2017-13-10T10:10:00"})
        member.update_from_dict(member_dict)

    # Invalid datetime format
    with pytest.raises(ValueError):
        member = Member()
        member_dict = dict(member_dict_sample)
        member_dict.update({"lastLoginTime": "InvalidDatetime"})
        member.update_from_dict(member_dict)

    # datetime might not have ending Z
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00.4546"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert (
        member_result_dict["lastLoginTime"]
        == "2017-10-10T10:10:00.004546+00:00"
    )

    # datetime containing ending Z
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00.4546Z"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert (
        member_result_dict["lastLoginTime"]
        == "2017-10-10T10:10:00.004546+00:00"
    )

    # datetime with timezone
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00.4546+03:00"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert (
        member_result_dict["lastLoginTime"]
        == "2017-10-10T10:10:00.004546+03:00"
    )

    # datetime without microsecond
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"lastLoginTime": "2017-10-10T10:10:00+03:00"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert member_result_dict["lastLoginTime"] == "2017-10-10T10:10:00+03:00"


def test_date_format():
    # iso date format
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"birth": "2001-01-01"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert member_result_dict["birth"] == "2001-01-01"

    # none iso date format
    with pytest.raises(ValueError):
        member = Member()
        member_dict = dict(member_dict_sample)
        member_dict.update({"birth": "01-01-01"})
        member.update_from_dict(member_dict)

    # none iso date format
    with pytest.raises(ValueError):
        member = Member()
        member_dict = dict(member_dict_sample)
        member_dict.update({"birth": "2001/01/01"})
        member.update_from_dict(member_dict)


def test_time_format():
    # iso time format
    member = Member()
    member_dict = dict(member_dict_sample)
    member_dict.update({"breakfastTime": "08:08:08"})
    member.update_from_dict(member_dict)
    member_result_dict = member.to_dict()
    assert member_result_dict["breakfastTime"] == "08:08:08"

    # none iso time format
    with pytest.raises(ValueError):
        member = Member()
        member_dict = dict(member_dict_sample)
        member_dict.update({"breakfastTime": "08-08-08"})
        member.update_from_dict(member_dict)
