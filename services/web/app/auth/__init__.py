from functools import wraps
import json
from urllib.request import urlopen
from flask import request, current_app
from jwt import get_unverified_header, decode, ExpiredSignatureError
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend


AUTH0_JWKS_URL = "https://dev-1ealnulz.us.auth0.com/.well-known/jwks.json"
CLIENT_ID = "mZMpAtQauzi8H9yPVgJkr31H8ZVfPyri"

def require_auth(f):
    @wraps(f)
    def decorator(**kwargs):
        user = get_user()
        current_app.logger.info("Successfully authenticated request for user: %s", user['sub'])
        return f(user, **kwargs)

    return decorator

def get_user():
    token = get_token()
    return verify_token(token)

def get_token():
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'authorization_header_missing',
            'decription': 'Authorization header is expected'
        }, 401)

    auth_header = request.headers['Authorization']
    auth_header_splits = auth_header.split()

    if auth_header_splits[0].lower() != "bearer":
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Authorization header must start with: "Bearer"'
        }, 401)

    if len(auth_header_splits) == 1:
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Authentication header token not found'
        }, 401)

    if len(auth_header_splits) > 2:
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Authentication header must be: "Bearer token"'
        }, 401)

    token = auth_header_splits[1]
    return token

def verify_token(token):
    try:
        unverified_header = get_unverified_header(token)
    except Exception:
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Invalid header, use RS256 singed JWT Access Token'
        }, 401)

    signing_keys = get_signing_keys()
    rsa_key = get_signing_key(signing_keys, unverified_header)

    try:
        return decode(token, rsa_key, algorithms=["RS256"], audience=CLIENT_ID)
    except ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'decription': 'The token has expired'
        }, 401)
    except Exception as ex:
        current_app.logger.error(ex)
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Unable to parse authentication token'
        }, 401)

def get_signing_keys():
    jsonurl = urlopen(AUTH0_JWKS_URL)
    response = json.load(jsonurl)

    if 'keys' not in response:
        raise Exception("The JWKS endpoint did not contain any keys")

    jwks = response['keys']
    signing_jwks = filter(check_valid_signing_key, jwks)

    if not signing_jwks:
        raise Exception("The JWKS endpoint did not contain any signing keys")
    
    return signing_jwks

def check_valid_signing_key(jwk):
    return (
        jwk['use'] == 'sig' 
        and jwk['kty'] == 'RSA'
        and jwk['alg'] == 'RS256'
        and jwk['n']
        and jwk['e']
        and jwk['kid']
        and (jwk['x5c'] and len(jwk['x5c']))
    )


def get_signing_key(signing_keys, unverified_header):
    rsa_key = {}
    for key in signing_keys:
        if key['kid'] == unverified_header['kid']:
            x5c = key['x5c'][0]
            rsa_key = cert_to_pem(x5c)
    if not rsa_key:
        raise AuthError({
            'code': 'invalid_auth_header',
            'decription': 'Unable to find approporiate key'
        }, 401)

    return rsa_key


def cert_to_pem(cert):
    cert_str = f"-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----"
    pem = load_pem_x509_certificate(cert_str.encode('utf-8'), default_backend())
    return pem.public_key()


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code