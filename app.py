from flask import Flask, render_template, request, redirect, url_for
import config as cf
from model import Item, ViewModel
from trello_app import trello_bp, login_manager
import session_items as session
import requests
import json
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config.from_pyfile('config.py')
    
    app.register_blueprint(trello_bp)
    login_manager.init_app(app)
        
    return app
