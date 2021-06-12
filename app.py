""" Autor: Robert Sołdyński"""



from flask import Flask, flash,request, render_template, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import shutil
from stats import analyse



app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filedata.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

static_need = ['static']

for i in static_need:
    if not os.path.exists(i):
        os.makedirs(i)


UPLOAD_FOLDER = './static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key="casdfnjakwhejfwefjkwnemwh87h"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(330), unique=True, nullable=False)
    size = db.Column(db.Float(), nullable=False)
    columns = db.Column(db.Integer(), nullable=False)
    rows = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return '<File %r>' % self.filename

db.create_all()



@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST' and request.files['myfile']:
        try:
            file = request.files.get('myfile')
            df = pd.read_csv(file, sep=';')
            row, column = df.shape
            if row>1000:
                flash("Plik musi zawierać mniej niż 1000 linii", "danger")
                return redirect('/')

            if column>20:
                flash("Plik musi mieć poniżej 20 kolumn ", "danger")
                return redirect('/')

            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename.split(".")[0])
            if not os.path.exists(path):
                File.query.filter_by(filename=filename).delete()
                os.mkdir(path)
            else:
                flash("Taki plik już istnieje", "danger")
                return redirect('/')

            file.save(os.path.join(path, filename))
            analyse(df, path)

            file.seek(0, os.SEEK_END)
            size = file.tell()
            
            fileinfo = File(filename=filename, size=size, columns=column, rows=row)
            db.session.add(fileinfo)
            db.session.commit()

            files = File.query.all()
            return render_template('index.html', files=files)

        except Exception as e:
            flash(e, "danger")
    files = File.query.all()
    return render_template('index.html', files=files)

#Opcja Usuwania Pików
@app.route("/deletefile/<id>")
def deletefile(id):
    exists = db.session.query(db.exists().where(File.id == id)).scalar()
    if exists:
        my_data = File.query.get(id)
        filename = my_data.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename.split(".")[0])
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

        db.session.delete(my_data)
        db.session.commit()
        flash("Plik usunięty poprawnie", "info")
    else:
        flash("Nie znaleziono pliku", "danger")

    return redirect('/')

#Podsumowanie
@app.route("/summary/<id>")
def summary(id):
    exists = db.session.query(db.exists().where(File.id == id)).scalar()
    if exists:
        my_data = File.query.get(id)
        filename = my_data.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename.split(".")[0])

        df = pd.read_csv(os.path.join(path,"result.csv"),sep=";")

        dfobj = df.dropna(subset=['Unique']).dropna(axis=1)
        dfnum = df.dropna(subset=['Min']).dropna(axis=1)
        dfdat = df.dropna(subset=['First Date']).dropna(axis=1)

        return render_template('summary.html', dfobj=dfobj, dfnum=dfnum, dfdat=dfdat, filedata = my_data)
    else:
        flash("Nie znaleziono pliku", "danger")

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)