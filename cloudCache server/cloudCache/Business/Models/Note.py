""" Contains Note SQLAlchemy model, and utility functions for manipulating these models. """

# pylint: disable=W0232,C0103
# disable no-init warning on Note model, and name-too-short warning on `id` variable

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils.types import ArrowType

from . import SQL_ALCHEMY_BASE, DB_SESSION as db
from . import Notebook
from ..Errors import NoteAlreadyExistsError

from arrow import now as arrow_now
from arrow.arrow import Arrow

from json import dumps

# -------------------------------------------------------------------------------------------------

class Note(SQL_ALCHEMY_BASE):
    """ Represents a cloudCache note. """

    __tablename__ = 'NOTE'

    id           = Column(Integer, primary_key=True)
    notebook_id  = Column(Integer, ForeignKey('NOTEBOOK.id'))
    key          = Column(String(255))
    value        = Column(String(255))
    created_on   = Column(ArrowType, default=arrow_now)
    last_updated = Column(ArrowType, default=arrow_now, onupdate=arrow_now)

    notebook = relationship(Notebook, backref=backref('notes'))


    def __repr__(self):
        self_repr = 'Note(notebook_id={nb_id}, key="{key}", value="{value}")'
        return self_repr.format(nb_id=self.notebook_id, key=self.key, value=self.value)

    def __str__(self):
        self_str = '[{nb_name}] {key} - {value}'
        return self_str.format(nb_name=self.notebook.name, key=self.key, value=self.value)


    def to_json(self, compact=True):
        """ Returns a JSON representation of this Note. """

        json = dict()
        attrs = ['id', 'notebook_id', 'key', 'value', 'created_on', 'last_updated']

        for attribute in attrs:
            attr_val = getattr(self, attribute)
            if isinstance(attr_val, Arrow):
                attr_val = str(attr_val.to('local'))
            json[attribute] = attr_val

        if compact:
            return dumps(json, separators=(',',':'))
        else:
            return dumps(json, indent=4, separators=(',', ': '))

# -------------------------------------------------------------------------------------------------

def create_note(key, value, notebook):
    """ Creates a Note entry in the database, and returns the Note object to the caller.

    Args:
        key (string): The new note's key.
        value (string): The new note's value.
        notebook (cloudCache.Business.Models.Notebook): The new note's notebook.

    Returns:
        cloudCache.Business.Models.Note: The newly-created Note.

    """

    if db.query(Note).filter_by(key=key, notebook=notebook).first():
        message = "A note with the key '{}' already exists for the notebook '{}'"
        message = message.format(key, notebook.name)
        raise NoteAlreadyExistsError(message)

    new_note = Note(key=key, value=value, notebook=notebook)

    db.add(new_note)
    db.commit()

    return new_note