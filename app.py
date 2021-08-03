from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
import sqlite3
from dotenv import load_dotenv
from livereload import Server

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"


class NewItemForm(FlaskForm):
    title = StringField("Title")
    price = StringField("Price")
    category = SelectField("Category", coerce=int)
    subcategory = SelectField("Subcategory", coerce=int)
    description = TextAreaField("Description")
    submit = SubmitField("Submit")


@app.route("/")
def home():
    conn = get_db()
    c = conn.cursor()

    items_from_db = c.execute("""
        SELECT
        i.id, i.title, i.price, i.description, i.image, c.name, s.name
        FROM 
        items AS i 
        INNER JOIN categories AS c on i.category_id = c.id
        INNER JOIN subcategories AS s ON i.subcategory_id = s.id
        ORDER BY i.id DESC
    """)

    items = []
    for row in items_from_db:
        item = {
            "id": row[0],
            "title": row[1],
            "price": row[2],
            "description": row[3],
            "image": row[4],
            "category": row[5],
            "subcategory": row[6]
        }
        items.append(item)

    return render_template('home.html', items=items)


@app.route("/item/new", methods=["GET", "POST"])
def new_item():
    conn = get_db()
    c = conn.cursor()
    form = NewItemForm()

    c.execute("SELECT id, name FROM categories")
    categories = c.fetchall()
    form.category.choices = categories

    c.execute("""SELECT id, name FROM subcategories WHERE category_id = ?""", (1, ))
    subcategories = c.fetchall()
    form.subcategory.choices = subcategories

    if form.validate_on_submit():
        c.execute("""
            INSERT INTO items 
            (title, description, price, image, category_id, subcategory_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
              form.title.data,
              form.description.data,
              float(form.price.data),
              "",
              form.category.data,
              form.subcategory.data
            )
        )
        conn.commit()
        flash(f"Item {request.form.get('title')} has been successfully submitted.", "success")
        return redirect(url_for('home'))

    if form.errors:
        flash(f"{form.errors}", "danger")

    return render_template("new_item.html", form=form)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("db/globomantics.db")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def main():
    server = Server(app.wsgi_app)
    server.serve(debug=False)


if __name__ == '__main__':
    main()
