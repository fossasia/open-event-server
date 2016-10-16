from flask import request, Blueprint, make_response
import datetime

app = Blueprint('babel', __name__)

@app.route('/choose_language', methods=('POST',))
def set_lang():
	l_code = request.form.get('l_code')
	response = make_response(l_code)
	expire_date = datetime.datetime.now()
	expire_date = expire_date + datetime.timedelta(days=60)
	response.set_cookie('selected_lang',value=l_code, expires=expire_date)
	return response
