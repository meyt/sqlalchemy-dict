
from sqlalchemy import Column
from sqlalchemy.orm import relationship as sa_relationship, composite as sa_composite


# noinspection PyAbstractClass
class Field(Column):

    def __init__(self,
                 *args,
                 dict_key=None,
                 readonly=None,
                 protected=None,
                 nullable=False,
                 info=None,
                 **kwargs):
        info = info or dict()

        if dict_key is not None:
            info['dict_key'] = dict_key

        if readonly is not None:
            info['readonly'] = readonly

        if protected is not None:
            info['protected'] = protected

        super(Field, self).__init__(*args, info=info, nullable=nullable, **kwargs)


def relationship(*args, dict_key=None, protected=None, **kwargs):
    info = dict()

    if dict_key:
        info['dict_key'] = dict_key

    if protected:
        info['protected'] = protected

    return sa_relationship(*args, info=info, **kwargs)


def composite(*args, dict_key=None, protected=None, readonly=None, **kwargs):
    info = dict()

    if dict_key:
        info['dict_key'] = dict_key

    if protected:
        info['protected'] = protected

    if readonly is not None:
        info['readonly'] = readonly

    return sa_composite(*args, info=info, **kwargs)
