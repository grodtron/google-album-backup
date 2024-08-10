"""
AR, 2018-10-25
Authorization class and get_credentials method for Google APIs
"""

# general imports
from oauth2client import file, client, tools
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

    def get_secret_client_config(self):
        region_name = "eu-north-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.client_secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        return get_secret_value_response['SecretString']


    @user_dir
    def get_credentials(self, **kwargs):
        """
        Method gets user credential from storage - JSON file
        If credential are not in storage or are invalid, gets new credentials
        If stored credential are expired, refreshes them

        :param kwargs: to send user directory between method and decorator
        :return: credentials
        """

        client_secret = self.get_secret_client_config()


        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_file:
            # Write the client_secrets content to the temporary file
            temp_file.write(client_secret)
            temp_file.flush()  # Ensure the content is written to disk

            flow = client.flow_from_clientsecrets(temp_file.name, self.scopes)
            creds = tools.run_flow(flow)
            return creds


"""
HELP:

About tools.run_flow:
'The new credentials are also stored in the storage argument, 
which updates the file associated with the Storage object.'
https://oauth2client.readthedocs.io/en/latest/source/oauth2client.tools.html

About OAuth2Credentials and refresh():
'Forces a refresh of the access_token' - and updates Storage object by storage 
argument of credentials (see tools.run_flow above). 
Storage argument is set by file.Storage.get(), when credentials are loaded
https://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2Credentials

"""
