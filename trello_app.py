from flask import Blueprint
from flask import current_app as app
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, LoginManager, current_user, login_user

from oauthlib.oauth2 import WebApplicationClient
from urllib.parse import urlencode

import config as cf
import session_roles as sr
import trello_mongo_db as mgdb
from model import Item, ViewModel, User

import session_items as session
import requests
import json
import uuid
import datetime

trello_bp = Blueprint( 'trello_bp', __name__)
login_manager = LoginManager()

@login_manager.unauthorized_handler
def unauthenticated():
  next_path = request.args.get('next')
  if current_user.is_authenticated:
    return redirect(next_path or url_for('index'))
  else:
    client = WebApplicationClient(cf.get_github_client_id())
    uri = cf.get_github_oauth_url()
    url_redirect = cf.get_github_call_back_url()
    state = client.state_generator()
    session['github_oauth_state'] = state
    session['next_path'] = next_path
    request_uri = client.prepare_request_uri(uri, redirect_uri=url_redirect, scope='user', state=state)
    return redirect(request_uri)


@trello_bp.route('/login/callback', methods=['GET', 'POST'])
def github_oauth_callback():
  client = WebApplicationClient(cf.get_github_client_id())
  client_secret = cf.get_github_client_secret()
  url_redirect = cf.get_github_call_back_url()
  code = client.parse_request_uri_response(request.url, session["github_oauth_state"]).get("code")
  body = client.prepare_request_body(code, redirect_uri=url_redirect, client_secret=client_secret)
  r1 = requests.post(cf.get_github_token_url, body)
  token_info = r1.json()
  access_token = token_info.get('access_token')
  expires_in = token_info.get('expires_in')

  url = cf.get_github_user_endpoint() + '?' + urlencode({"access_token": access_token})
  r2 = request.get(url)
  user_data = r2.json()
  id = user_data.get("login")
  name = user_data.get("name")
  email = user_data.get("email")
  user = User(id, name, email, expires_in)
  login_user(user)

  return redirect(request.args.get(session['next_path']))


@trello_bp.route('/', methods=['GET'])
@login_required
#@app.route('/')
def index():
    trello_col = mgdb.get_trello_collection()
    cards = list(trello_col.find())
    items_list = list()
    for card in cards:
        item = Item(card['_id'], card['status'], card['name'], card['_date'])
        items_list.append(item)

    item_view_model = ViewModel(items_list)
    return render_template('index.html', view_model=item_view_model, is_writer=is_writer(current_user.get_id()))


@trello_bp.route('/complete_item/<idCard>', methods=['GET', 'PUT', 'POST'])
@login_required
def update_card(idCard):
  if is_writer(current_user.get_id()):
    #trello_col = mgdb.get_trello_collection()
    mgdb.get_trello_collection().find_one_and_update(
        {"_id" : idCard},
        {"$set":
            {"status": "Done",
            "_date": datetime.now().strftime('%Y-%m-%d')}
        },upsert=True
    )

  return redirect(url_for('trello_bp.index'))
  


@trello_bp.route('/add', methods=['POST'])
@login_required
def add_card():
  if is_writer(current_user.get_id()):
    if request.form['title']:
        title = request.form['title']

    card = { "_id": str(uuid.uuid4()), "status": "To Do", "title": title, "_date": datetime.now().strftime('%Y-%m-%d') }
    mgdb.get_trello_collection().insert_one(card)
    return redirect(url_for('trello_bp.index'))
  else:
    return redirect(url_for('trello_bp.index'))


def is_writer(id):
  return sr.get_role(id) == 'writer'
