from flask import Flask
from flask_assets import Environment, Bundle

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('app/config.py')
assets = Environment(app)


js = Bundle( 'js/jquery-3.4.1.min.js',
             'js/highstock.js',
             'js/bootstrap.js',
             'js/bootstrap-notify.js',
             filters='jsmin',
             output='gen/josien.js')

css = Bundle( 'css/bootstrap.css',
              'css/navbar-top-fixed.css',
              'css/josien.css',
              filters='cssmin',
              output='gen/josien.css')


assets.register('js_all', js)
assets.register('css_all', css)

from app.views import *
