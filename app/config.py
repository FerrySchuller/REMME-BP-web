import os
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', 'xo')
WTF_CSRF_SECRET_KEY = 'xxxx'
