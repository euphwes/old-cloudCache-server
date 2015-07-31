""" Module for the NotebookHandler class in the cloudCache REST API. """

from tornado.escape import json_decode

from . import AuthorizeHandler

from cloudCache.Business.Models import User, Notebook, DB_SESSION as db
from cloudCache.Business.Models.Note import create_note
from cloudCache.Business.Models.Notebook import get_notebook
from cloudCache.Business.Errors import NoteAlreadyExistsError, NotebookDoesntExistError

# -------------------------------------------------------------------------------------------------

# /notebooks/{notebook}/notes/{note}

class NoteHandler(AuthorizeHandler):
    """ The request handler for managing cloudCache notes. """


    def post(self, **kwargs):
        """ Implements the HTTP POST call on /notebooks/{notebook}/notes. The user must
        provide an HTTP body of the type application/json, with the following format:

        {
            'note_key': 'My awesome note',
            'note_value': 'The contents of my awesome note'
        }

        Returns the note ID if successful, or an error message otherwise. """

        self.authorize()

        info = json_decode(self.request.body)

        try:
            note_key   = info['note_key']
            note_value = info['note_value']
            notebook   = get_notebook(kwargs['notebook'], self.current_user)

            note = create_note(note_key, note_value, notebook)
            response = {'note_id': note.id}

        except NoteAlreadyExistsError as e:
            self.set_status(409) # Conflict
            response = {'message': str(e)}

        except NotebookDoesntExistError as e:
            self.set_status(404) # Not Found
            response = {'message': str(e)}

        except KeyError:
            self.set_status(400) # Bad Request
            message = 'Invalid POST body. Must include note_key and note_value.'
            response = {'message': message}

        self.write(response)