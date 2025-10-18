from flask_wtf import FlaskForm
from wtforms import StringField , validators


class DbSearch(FlaskForm):
    dataBase = StringField('Baza danych', validators=[validators.data_required])
    tableName = StringField('Nazwa tabeli', validators=[validators.data_required])
    columnName = StringField('Nazwa kolumnu',validators=[validators.data_required])
   

