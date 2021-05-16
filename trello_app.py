from flask import Blueprint
from flask import current_app as app
from flask import Flask, render_template, request, redirect, url_for
import config as cf
import trello_mongo_db as mgdb
from model import Item, ViewModel

import session_items as session
import requests
import json
import uuid
import datetime

trello_bp = Blueprint( 'trello_bp', __name__)

@trello_bp.route('/', methods=['GET'])
#@app.route('/')
def index():
    trello_col = mgdb.get_trello_collection()
    cards = list(trello_col.find())
    items_list = list()
    for card in cards:
        item = Item(card['_id'], card['status'], card['name'], card['_date'])
        items_list.append(item)

    item_view_model = ViewModel(items_list)
    return render_template('index.html', view_model=item_view_model)


@trello_bp.route('/complete_item/<idCard>', methods=['GET', 'PUT', 'POST'])
#@app.route('/complete_item/<idCard>', methods=['GET', 'PUT'])
def update_card(idCard):

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
#@app.route('/add', methods=['POST'])
def add_card():
    if request.form['title']:
        title = request.form['title']

    card = { "_id": str(uuid.uuid4()), "status": "To Do", "title": title, "_date": datetime.now().strftime('%Y-%m-%d') }
    mgdb.get_trello_collection().insert_one(card)
    return redirect(url_for('trello_bp.index'))


def add_card_to_todo():
        add_card()


def add_card_to_done():
    add_card()


#delete card/item
def remove_card(id):
    result = mgdb.get_trello_collection().find_one_and_delete({"_id": id})
    print (result.value())


#Fetch Cards on a list
def get_cards(id):
    result = mgdb.get_trello_collection().find({"_id": id})
    print (result.value())


# create lists
def add_list_to_board():
    trello_list = mgdb.get_trello_collection()
    print(trello_list)


#Create New Board
#def create_to_do_board(board_name = 'MyCorndelDevOpsToDoBoard'):
def create_to_do_board():
    trello_board = mgdb.get_trello_db()
    print(trello_board)