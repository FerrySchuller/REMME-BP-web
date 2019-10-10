from flask import Flask
from flask_assets import Environment, Bundle

app = Flask(__name__, instance_relative_config=True)
assets = Environment(app)


js = Bundle( 'js/jquery-3.1.1.min.js',
             'js/bootstrap.js',
             'js/highstock.js',
             'js/highmaps.js',
             'js/data.js',
             'js/exporting.js',
             'js/export-data.js',
             'js/josien.js',
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
