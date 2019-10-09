from flask import Flask, jsonify, Response, redirect, request, render_template
from flask_assets import Environment, Bundle

app = Flask(__name__, instance_relative_config=True)
assets = Environment(app)


js = Bundle( 'js/bootstrap.js',
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
