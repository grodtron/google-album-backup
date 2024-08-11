from flask import Flask, redirect, request, session, url_for
from oauth2client.client import OAuth2WebServerFlow

"""
This is a very quick and dirty way of getting the required OAuth tokens that will ultiimately
be stored in AWS Secrets Manager. This just allows us to open localhost:12358 and redirect through
the OAuth flow.
"""

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Replace these with your client_id and client_secret
CLIENT_ID = 'TODO'
CLIENT_SECRET = 'TODO'
REDIRECT_URI = 'http://localhost:12358/oauth2callback'

flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope='https://www.googleapis.com/auth/photoslibrary.readonly',
                           redirect_uri=REDIRECT_URI)

@app.route('/')
def index():
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    credentials = flow.step2_exchange(code)

    # Save the credentials for future use
    session['credentials'] = credentials.to_json()

    # TODO - more elegant way of printing out the relevant parts
    print(repr(credentials.to_json()))

    return 'Authorization complete. You can close this window.'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12358)


