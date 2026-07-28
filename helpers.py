from functools import wraps
from flask_login import current_user
from flask import abort

#### decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


#### filters
def datetimeformat(value, string_format='%B %d, %Y'):
    return value.strftime(string_format)