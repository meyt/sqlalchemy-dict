
from sqlalchemy import Column
from sqlalchemy.orm import (
    relationship as sa_relationship,
    composite as sa_composite,
    synonym as sa_synonym
)


# noinspection PyAbstractClass
class Field(Column):
    """
    An overridden class from ``sqlalchemy.Column`` to apply ``sqlalchemy_dict`` properties.
    """

    def __init__(self, *args, dict_key: str=None, readonly: bool=None,
                 protected: bool=None, info: dict=None, **kwargs):
        """
        Initialize the field

        :param args: Positional-arguments that directly pass into ``sqlalchemy.Column.__init__``
        :param dict_key: Custom dictionary key related to this field, as default it
                         will reads the field name and format
                         (using ``sqlalchemy_dict.BaseModel.__formatter__``) it before export.
        :param readonly: Make field read-only, it's mean this field will not accept any value from
                         ``sqlalchemy_dict.BaseModel.update_from_dict`` input dictionary.
        :param protected: Make field protected to representation
        :param info: Pass into Column info
        :param kwargs: Keyword-arguments that directly pass into  ``sqlalchemy.Column.__init__``
        """
        info = info or dict()

        if dict_key is not None:
            info['dict_key'] = dict_key

        if readonly is not None:
            info['readonly'] = readonly

        if protected is not None:
            info['protected'] = protected

        super(Field, self).__init__(*args, info=info, **kwargs)


def relationship(*args, dict_key: str=None, protected: bool=None, **kwargs):
    """
    Same as ``sqlalchemy.orm.relationship`` with extra arguments to use in ``sqlalchemy_dict``.

    :param args: Positional-arguments that directly pass into ``sqlalchemy.orm.relationship``.
    :param dict_key: Custom dictionary key.
                     default is formatted (using ``sqlalchemy_dict.BaseModel.__formatter__``)
                     attribute name (where ``relationship`` called).
    :param protected: Make field protected to representation.
    :param kwargs: Keyword-arguments that directly pass into ``sqlalchemy.orm.relationship``.
    :return:
    """
    info = dict()

    if dict_key is not None:
        info['dict_key'] = dict_key

    if protected is not None:
        info['protected'] = protected

    return sa_relationship(*args, info=info, **kwargs)


def composite(*args, dict_key: str=None, protected: bool=None, readonly: bool=None, **kwargs):
    """
    Same as ``sqlalchemy.orm.composite`` with extra arguments to use in ``sqlalchemy_dict``.

    :param args: Positional-arguments that directly pass into ``sqlalchemy.orm.composite``.
    :param dict_key: Custom dictionary key.
                     default is formatted (using ``sqlalchemy_dict.BaseModel.__formatter__``)
                     attribute name (where ``composite`` called).
    :param protected:  Make field protected to representation.
    :param readonly: Make field read-only, it's mean this field will not accept any value from
                     ``sqlalchemy_dict.BaseModel.update_from_dict`` input dictionary.
    :param kwargs: Keyword-arguments that directly pass into ``sqlalchemy.orm.composite``.
    :return:
    """
    info = dict()

    if dict_key is not None:
        info['dict_key'] = dict_key

    if protected is not None:
        info['protected'] = protected

    if readonly is not None:
        info['readonly'] = readonly

    return sa_composite(*args, info=info, **kwargs)


def synonym(*args, dict_key: str=None, protected: bool=None, readonly: bool=None, **kwargs):
    """
    Same as ``sqlalchemy.orm.synonym`` with extra arguments to use in ``sqlalchemy_dict``.

    :param args: Positional-arguments that directly pass into ``sqlalchemy.orm.synonym``.
    :param dict_key: Custom dictionary key.
                     default is formatted (using ``sqlalchemy_dict.BaseModel.__formatter__``)
                     attribute name (where ``synonym`` called).
    :param protected:  Make field protected to representation.
    :param readonly: Make field read-only, it's mean this field will not accept any value from
                     ``sqlalchemy_dict.BaseModel.update_from_dict`` input dictionary.
    :param kwargs: Keyword-arguments that directly pass into ``sqlalchemy.orm.synonym``.
    :return:
    """
    info = dict()

    if dict_key is not None:
        info['dict_key'] = dict_key

    if protected is not None:
        info['protected'] = protected

    if readonly is not None:
        info['readonly'] = readonly

    return sa_synonym(*args, info=info, **kwargs)
