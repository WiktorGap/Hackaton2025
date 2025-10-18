from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/ludzie')
def ludzie():
    return render_template('ludzie.html')

@main.route('/transport')
def transport():
    return render_template('transport.html')

@main.route('/srodowisko')
def srodowisko():
    return render_template('srodowisko.html')

@main.route('/budzet')
def budzet():
    return render_template('budzet.html')
