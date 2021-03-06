import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

import re, ast


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# from r"['[타이어 마찰음]\n', '오직 도깨비 신부만이\n', '\n']"
# to [타이어 마찰음], 오직 도깨비 신부만

def prettify(raw_str):
    subtitle_list = ast.literal_eval(raw_str)
    processed_str = ''
    for subtitle in subtitle_list:
        subtitle = re.sub(r'\n', '', subtitle)
        processed_str += subtitle
    return processed_str
