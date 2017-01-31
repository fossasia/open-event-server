from . import api
from flask import Flask,render_template, redirect, request, url_for,session,escape
# from .form import User
#import MySQLdb
#from db_connect import connection
from functools import wraps
from config import config


#import config
from flask_login import current_user
from app.models import registration_form
from app import db


@api.route('/events/<int:event_id>/registartion_form/',methods=['GET','POST'])
def register():
    error=None
    if request.method == 'POST':
        user = registration_form()
        user.firstname = request.form['firstname']
        user.email = request.form['email']
        user. lastname = request.form['lastname']

        if registration_form.query.filter_by(firstname=user.firstname).first():
            error="Username Already exists"
        else:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('api.extras_celery_task',username = user.username))
    return render_template("registration_form.html",error=error)
