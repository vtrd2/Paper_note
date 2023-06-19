from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class NoteEditor(FlaskForm):
    note = TextAreaField('', validators=[DataRequired(), Length(1, 64)])
    # urgent = BooleanField('Urgent', render_kw={'id': f'urgent-boolean'})
    submit = SubmitField('Commit')