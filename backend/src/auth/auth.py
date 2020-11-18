from flask import request, _request_ctx_stack, abort
from functools import wraps
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

access_token='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9HMUtKb25xN3VXSEZ4ejlGVjFaeSJ9.eyJpc3MiOiJodHRwczovL29tYXJlbHNoZWVraC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTE0MjYxMjM1MjE3NTQyMDM0MTQiLCJhdWQiOiJ0ZXN0IiwiaWF0IjoxNjA1NzIxODA3LCJleHAiOjE2MDU3MjkwMDcsImF6cCI6IlRIcXZYaHVtMmY4bnZuQlk5ekhtMnN3VlRFa1hkVjBhIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.m9EJSKVVx9WdixgzOqdOqf1sS2fJbYSl5EluaveIoSKIKRSOhxd5yyYDL-qOFGRZpTheVoKSd56Sxc3WpAYOno5vwqBaMYHzEIohPuNKwMoeEniVePZ_J3OZVpMIAm0DM9VRlw5VnCQjvS2AHdSYcOn4smMiOQGMhPsdUVhXd1FX3KQASCSlHsYvyJuYcmTnFDcgkpgyUa6FrWKJax_0DtkyiqNFdaT3fv2F3gii5-4Pyixj8JkCLnsKb0E_lhRroah9ZgqqwPrJsk5ezqVtc7oatdEo1M1p0GfY8trydXatmqhqyq_kccTNZuWWGAYupXvSDwecLEvjCDNkbw33jA'
AUTH0_DOMAIN = 'omarelsheekh.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'test'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

## Auth Header

'''
implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    if 'Authorization' not in request.headers:
            raise AuthError('No Authorization header in the request',401)
    auth=request.headers['Authorization'].split(' ')
    if len(auth) !=2:
        raise AuthError('token error',401)
    elif auth[0].lower() !='bearer':
        raise AuthError('token error',401)
    return auth[1]

'''
implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError('Permissions not included in JWT.', 400)

    if permission not in payload['permissions']:
        raise AuthError('Permissions not included in JWT.', 403)
    return True

'''
implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            return payload
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
'''
implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(f, permission=None):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            if permission:
                check_permissions(permission, payload)
        except AuthError as e:
            abort(e.status_code)
        return f(*args, **kwargs)

    return wrapper
