
import json
from tastypie.exceptions import TastypieError
from tastypie.http import HttpBadRequest
import re

MINIMUM_PASSWORD_LENGTH = 6
REGEX_VALID_PASSWORD = (
    ## Don't allow any spaces, e.g. '\t', '\n' or whitespace etc.
    r'^(?!.*[\s])'
    ## Check for a digit
    '((?=.*[\d])'
    ## Check for an uppercase letter
    '(?=.*[A-Z])'
    ## check for special characters. Something which is not word, digit or
    ## space will be treated as special character
    '(?=.*[^\w\d\s])).'
    ## Minimum 8 characters
    '{' + str(MINIMUM_PASSWORD_LENGTH) + ',}$')


def validate_password(password):
    if re.match(REGEX_VALID_PASSWORD, password):
        return True
    return False


class CustomBadRequest(TastypieError):
    '''
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.
    Required after upgrading to django-tastypie==0.9.14
    '''

    def __init__(self, code='', message=''):
        self._response = {
            'error': {'code': code or 'not_provided',
                      'message': message or 'No error message was provided.'}}

    @property
    def response(self):
        return HttpBadRequest(
            json.dumps(self._response),
            content_type='application/json')


