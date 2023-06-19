from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from . import main
from .forms import NoteEditor
from ..models import Note
from .. import db

@main.route('/')
def index():
    dict_notes = {}
    try:
        notes = current_user.notes
        notes = sorted(notes, key=lambda note: note.id)
    except Exception:
        notes = []
    for value in range(18):
        try:
            dict_notes[value] = notes[value]
        except IndexError:
            dict_notes[value] = ''
    
    return render_template('note_area.html', notes=dict_notes)

@main.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    notes = list(current_user.notes)
    if len(notes) >= 18:
        flash('Your paper is full')
        return redirect('/')

    form = NoteEditor()

    if form.validate_on_submit():
        new_note = Note(body=form.note.data, author=current_user)
        db.session.add(new_note)
        db.session.commit()
        flash('The new note have been added')
        return redirect('/')

    return render_template('new_note.html', form=form)

@main.route('/note/<note_id>', methods=['GET', 'POST'])
@login_required
def note(note_id):
    current_user_id_notes = [note.id for note in current_user.notes]
    try:
        note_id = int(note_id)
    except ValueError:
        abort(404)
        # flash('Not allowed')
        # return redirect('/') #redirecionar para pagina de não autorizado mais tarde
    if note_id not in current_user_id_notes:
        abort(404)
        # flash('Not allowed')
        # return redirect('/') #redirecionar para pagina de não autorizado mais tarde
    
    form = NoteEditor()
    note_is_scratched = Note.query.get(note_id).scratched

    if form.validate_on_submit():
        if form.note.data.strip() == '':
            flash("You can't save a note to nothing")
            return redirect(f'{note_id}')
        if note_is_scratched:
            flash("You can't edit a scratched note")
            return redirect(f'{note_id}')
        Note.query.get(note_id).body = form.note.data 
        db.session.commit()
        flash('The changes have been saved')
        return redirect('/')
    
    else:
        form.note.data = Note.query.get(note_id).body

    return render_template('note.html', note_id=note_id, note_is_scratched=note_is_scratched, form=form)

@main.route('/scratch/<note_id>', methods=['GET', 'POST'])
@login_required
def scratch(note_id):
    current_user_id_notes = [note.id for note in current_user.notes]
    try:
        note_id = int(note_id)
    except ValueError:
        flash('Not allowed')
        return redirect('/') #redirecionar para pagina de não autorizado mais tarde
    if note_id not in current_user_id_notes:
        flash('Not allowed')
        return redirect('/')
    
    note = Note.query.get(note_id)
    if note.scratched:
        note.scratched = False
        db.session.commit()
        flash('Your note have been unscratched')
    else:
        note.scratched = True
        db.session.commit()
        flash('Your note have been scratched')
    return redirect('/')

@main.route('/clear_notes', methods=['GET', 'POST'])
@login_required
def clear_notes():
    scratched_notes = Note.query.filter_by(author_id=current_user.id, scratched=True)
    if list(scratched_notes):
        Note.clear(scratched_notes)
        flash('Scratched notes have been deleted')
    else:
        flash("No scratched notes to delete")
    return redirect('/')