from requests_oauthlib import OAuth2Session
from .utils import load_config
import webbrowser
import urllib.parse

def authenticate():
    config = load_config('auth0_config.json')  # Load from config
    oauth = OAuth2Session(
        config['client_id'],
        redirect_uri=config['redirect_uri'],
        scope=config['scope']
    )
    authorization_url, state = oauth.authorization_url(
        f"https://{config['domain']}/authorize"
    )
    print(f"Please go to this URL and authorize: {authorization_url}")
    webbrowser.open(authorization_url)  # Open browser automatically

    # Simplified callback handling (for desktop; in production, use local server)
    auth_code = input("Enter the full callback URL: ").strip()
    if 'code=' in auth_code:
        url_parts = urllib.parse.urlparse(auth_code)
        query_params = urllib.parse.parse_qs(url_parts.query)
        auth_code = query_params.get('code', [None])[0]
        if auth_code:
            token = oauth.fetch_token(
                f"https://{config['domain']}/oauth/token",
                code=auth_code,
                client_secret=config['client_secret']
            )
            print("Authentication successful! Token:", token['access_token'])
            return token
    print("Authentication failed.")
    return None  # Or raise exception

# For testing: Bypass auth
def test_auth():
    return {'access_token': 'test_token', 'user': 'test_user'}

if __name__ == "__main__":
    token = authenticate()
    if token:
        print("Auth token obtained.")