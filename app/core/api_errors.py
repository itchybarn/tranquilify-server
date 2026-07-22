"""Central catalog of the APIErrors raised across the app.

Import and raise these helpers instead of constructing APIError inline, so the
status codes, error codes, and user-facing messages all live in one place. Each
is a small factory returning a fresh APIError, e.g. `raise invalid_credentials()`.
"""
from app.core.errors import APIError


# -- tokens / sessions --

def token_expired() -> APIError:
    return APIError(status=401, code="token_expired", message="Access token has expired.")

def invalid_token() -> APIError:
    return APIError(status=401, code="invalid_token", message="Credentials could not be validated.")

def invalid_refresh_token() -> APIError:
    return APIError(status=401, code="invalid_refresh_token", message="Refresh token is invalid, revoked, or expired.")


# -- credentials / passwords --

def invalid_credentials() -> APIError:
    return APIError(status=401, code="invalid_credentials", message="Invalid username or password")

def incorrect_current_password() -> APIError:
    return APIError(status=403, code="invalid_credentials", message="Current password is incorrect")


# -- users --

def user_not_found(message: str = "No user found") -> APIError:
    return APIError(status=404, code="user_not_found", message=message)

def username_taken() -> APIError:
    return APIError(status=409, code="username_taken", message="That username is already taken")


# -- verification codes --

def code_incorrect() -> APIError:
    return APIError(status=403, code="code_incorrect", message="The code is incorrect or has expired.")

def code_delivery_failed() -> APIError:
    return APIError(status=403, code="code_delivery_failed", message="Unable to send a code to your auth method")

# -- login --

def invalid_login_method() -> APIError:
    return APIError(status=403, code="invalid_login_method", message="The login_method you provided is not supported")