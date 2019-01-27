Guide
=====


Usage
-----

First of all we'll setup :func:`BaseModel <sqlalchemy_dict.base_model.BaseModel>`
as base class for sqlalchemy ``DeclarativeBase``:

.. code-block:: python

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.sql.schema import MetaData
    from sqlalchemy_dict import BaseModel

    metadata = MetaData()
    DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)

this will add extra functionality to all models,
and then for add some extra information to model fields, we should use

- :func:`sqlalchemy_dict.field.Field` instead of ``sqlalchemy.Column``
- :func:`sqlalchemy_dict.field.relationship` instead of ``sqlalchemy.orm.relationship``
- :func:`sqlalchemy_dict.field.composite` instead of ``sqlalchemy.orm.composite``
- :func:`sqlalchemy_dict.field.synonym` instead of ``sqlalchemy.orm.synonym``


Here is a full example:

.. code-block:: python

    from sqlalchemy import Integer, Unicode, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.sql.schema import MetaData

    from sqlalchemy_dict import BaseModel, Field, relationship, composite, synonym

    metadata = MetaData()
    DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)

    # Sample compositor
    class FullName(object):
        def __init__(self, first_name, last_name):
            self.first_name = first_name
            self.last_name = last_name

        def __composite_values__(self):
            return '%s %s' % (self.first_name, self.last_name)

        def __repr__(self):
            return 'FullName(%s %s)' % (self.first_name, self.last_name)

        def __eq__(self, other):
            return isinstance(other, FullName) and \
                   other.first_name == self.first_name and \
                   other.last_name == self.last_name

        def __ne__(self, other):
            return not self.__eq__(other)


    class Member(DeclarativeBase):
        __tablename__ = 'member'

        id = Field(Integer, primary_key=True)
        email = Field(Unicode(100), unique=True, index=True)
        first_name = Field(Unicode(50), index=True)
        last_name = Field(Unicode(100), dict_key='lastName')
        full_name = composite(FullName, first_name, last_name, readonly=True, dict_key='fullName')
        _password = Field('password', Unicode(128), index=True, protected=True)
        assigner_id = Field(Integer, ForeignKey('member.id'), nullable=True)
        assigner = relationship('Member', uselist=False)

        def _set_password(self, password):
            self._password = 'hashed:%s' % password

        def _get_password(self):  # pragma: no cover
            return self._password

        password = synonym(
            '_password',
            descriptor=property(_get_password, _set_password),
            protected=True
        )

Now you can import/export values from/to model:


.. code-block:: python

    >>> member = Member()
    >>> # Import from dictionary
    >>> member.update_from_dict({
    ...     'firstName': 'John',
    ...     'lastName': 'Doe',
    ...     'password': '123456',
    ...     'email': 'john@doe.com'
    ... })
    >>> # Export as dictionary
    >>> member.to_dict()
    {'firstName': 'John', 'lastName': 'Doe', 'password': '123456', 'email': 'john@doe.com'}

Access rights
-------------

``sqlalchemy-dict`` have two access options for model
properties (
:func:`Field <sqlalchemy_dict.field.Field>`,
:func:`relationship <sqlalchemy_dict.field.relationship>`,
:func:`composite <sqlalchemy_dict.field.composite>`,
:func:`synonym <sqlalchemy_dict.field.synonym>`) to control what should import/export.

- ``readonly``: Make property just readonly and will not update values from input dictionary.
- ``protected``: Will remove a field from output dictionary.


Query dumping
-------------

Queries can easily dump with :func:`dump_query <sqlalchemy_dict.base_model.BaseModel.dump_query>` method:

.. code-block:: python

    all_mikes_list = Member.dump_query(
        Member.query.filter(Member.first_name.like('mike'))
    )

or using :func:`expose <sqlalchemy_dict.base_model.BaseModel.expose>` decorator:


.. code-block:: python

    @Member.expose
    def get_all_mikes():
        return Member.query.filter(Member.first_name.like('mike'))
