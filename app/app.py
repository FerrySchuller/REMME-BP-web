from flask import Flask
from flask_assets import Environment, Bundle

#app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__)
app.config.from_pyfile('config.py')
assets = Environment(app)


js = Bundle( 'js/jquery-3.4.1.min.js',
             #'js/jquery-3.3.1.min.js',
             'js/popper.min.js',
             'js/highstock.js',
             'js/bootstrap.js',
             'js/bootstrap-notify.js',
             'js/bootstrap-table.min.js',
             'js/bootstrap-table-auto-refresh.min.js',
             'js/datatables.js',
             'js/dark-blue.js',
             'js/josien.js',
             filters='jsmin',
             output='gen/josien.js')

css = Bundle( 'css/bootstrap.css',
              'css/navbar-top-fixed.css',
              'css/Chart.css',
              'css/animate.css',
              'css/fontawesome.css',
              'css/bootstrap-table.min.css',
              'css/datatables.css',
              'css/josien.css',
              filters='cssmin',
              output='gen/josien.css')


assets.register('js_all', js)
assets.register('css_all', css)

from app.views import *
