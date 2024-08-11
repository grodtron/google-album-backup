"""
AR, 2018-10-25
Authorization class and get_credentials method for Google APIs
"""

# general imports
from oauth2client import file, client, tools
from oauth2client.client import OAuth2Credentials
import httplib2
import os
import boto3
import json
from botocore.exceptions import ClientError
import tempfile

# local imports
from userdir import user_dir


class Auth:
    def __init__(self, scopes, client_secret_name):
        self.scopes = scopes
        self.client_secret_name = client_secret_name


    def get_credentials(self):
        # TODO - retrieve from secrets manager
        # Assuming you've already obtained these from the first interaction
        refresh_token =  1.0/0.0
        client_id = 1.0/0.0
        client_secret = 1.0/0.0
        token_uri = "https://oauth2.googleapis.com/token"

        credentials = OAuth2Credentials(
            access_token=None,  # Start with no access token
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri=token_uri,
            user_agent=None,
            revoke_uri=None
        )

        # http = credentials.authorize(httplib2.Http())

        # The credentials object will handle refreshing the token automatically
        # when you use it with an API request

        return credentials
