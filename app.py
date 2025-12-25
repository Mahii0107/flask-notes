from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my-secret')
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')


os.makedirs(instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'notes.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='owner', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.relationship('Note', backref='category', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.relationship('Tag', secondary='note_tags', backref='notes')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

note_tags = db.Table('note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        # Create default categories for new user
        default_categories = [
            Category(name='Personal', color='#007bff', user_id=new_user.id),
            Category(name='Work', color='#28a745', user_id=new_user.id),
            Category(name='Ideas', color='#ffc107', user_id=new_user.id),
        ]
        db.session.add_all(default_categories)
        db.session.commit()
        
        # Log user in
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Notes Routes (Protected)
@app.route('/')
@login_required
def index():
    user_id = session['user_id']
    notes = Note.query.filter_by(user_id=user_id).all()
    categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('index.html', notes=notes, categories=categories)

@app.route('/note/new', methods=['GET', 'POST'])
@login_required
def create_note():
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        is_pinned = request.form.get('is_pinned') == 'on'
        tags_input = request.form.get('tags', '')
        
        note = Note(
            title=title,
            content=content,
            category_id=category_id if category_id else None,
            user_id=user_id,
            is_pinned=is_pinned
        )
        
        # Handle tags
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)
        
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('index'))
    
    categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('create_note.html', categories=categories)

@app.route('/note/<int:id>')
@login_required
def view_note(id):
    user_id = session['user_id']
    note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
    return render_template('view_note.html', note=note)

@app.route('/note/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    user_id = session['user_id']
    note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    if request.method == 'POST':
        note.title = request.form.get('title')
        note.content = request.form.get('content')
        note.category_id = request.form.get('category_id') if request.form.get('category_id') else None
        note.is_pinned = request.form.get('is_pinned') == 'on'
        note.updated_at = datetime.utcnow()
        
        # Update tags
        note.tags.clear()
        tags_input = request.form.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)
        
        db.session.commit()
        return redirect(url_for('view_note', id=note.id))
    
    categories = Category.query.filter_by(user_id=user_id).all()
    tags_str = ', '.join([tag.name for tag in note.tags])
    return render_template('edit_note.html', note=note, categories=categories, tags_str=tags_str)

@app.route('/note/<int:id>/delete', methods=['POST'])
@login_required
def delete_note(id):
    user_id = session['user_id']
    note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/note/<int:id>/toggle-pin', methods=['POST'])
@login_required
def toggle_pin(id):
    user_id = session['user_id']
    note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
    note.is_pinned = not note.is_pinned
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/categories')
@login_required
def categories():
    user_id = session['user_id']
    all_categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('categories.html', categories=all_categories)

@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')
        
        category = Category(name=name, color=color, user_id=user_id)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('categories'))
    
    return render_template('create_category.html')


# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

