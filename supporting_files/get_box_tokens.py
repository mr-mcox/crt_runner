from boxsdk import OAuth2, Client
client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'


def store_tokens(access_token, refresh_token):
    at = open('box_access_token.txt', 'w')
    rt = open('box_refresh_token.txt', 'w')
    at.write(access_token)
    rt.write(refresh_token)
    at.close()
    rt.close()

oauth = OAuth2(
    client_id=client_id,
    client_secret=client_secret,
    store_tokens=store_tokens,
)

auth_url, csrf_token = oauth.get_authorization_url('http://0.0.0.0')
print("Go to: " + auth_url)
auth_code = input("Enter code:")
access_token, refresh_token = oauth.authenticate(auth_code)

client = Client(oauth)