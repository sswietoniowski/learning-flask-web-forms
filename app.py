from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length
import sqlite3
from dotenv import load_dotenv
from livereload import Server

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"


class ItemForm(FlaskForm):
    title = StringField("Title",
                        validators=[InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=5, max=20,
                                           message="Input must be between 5 and 20 characters long.")])

    price = DecimalField("Price")
    description = TextAreaField("Description",
                                validators=[InputRequired("Input is required!"),
                                            DataRequired("Data is required!"),
                                            Length(min=5, max=40,
                                                   message="Input must be between 5 and 20 characters long.")])


class NewItemForm(ItemForm):
    category = SelectField("Category", coerce=int)
    subcategory = SelectField("Subcategory", coerce=int)
    submit = SubmitField("Submit")


class EditItemForm(ItemForm):
    submit = SubmitField("Update item")


class DeleteItemForm(FlaskForm):
    submit = SubmitField("Delete item")


@app.route("/item/<int:item_id>")
def item(item_id):
    conn = get_db()
    c = conn.cursor()

    items_from_db = c.execute("""
        SELECT i.id, i.title, i.description, i.price, i.image, c.name, s.name
        FROM items AS i
        INNER JOIN categories AS c ON c.id = i.category_id
        INNER JOIN subcategories AS s ON s.id = i.subcategory_id
        WHERE i.id = ?
    """, (item_id, ))
    row = c.fetchone()

    try:
        item = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": row[3],
            "image": row[4],
            "category": row[5],
            "subcategory": row[6]
        }
    except:
        item = {}

    if item:
        delete_item_form = DeleteItemForm()

        return render_template("item.html", item=item, delete_item_form=delete_item_form)

    return redirect(url_for("home"))


@app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db()
    c = conn.cursor()

    item_from_db = c.execute("""
        SELECT i.id, i.title, i.description, i.price, i.image 
        FROM items AS i
        WHERE i.id = ?
    """, (item_id,))
    row = c.fetchone()
    try:
        item = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": row[3],
            "image": row[4]
        }
    except:
        item = {}

    if item:
        form = EditItemForm()
        if form.validate_on_submit():
            c.execute("""
                UPDATE items
                SET title = ?, description = ?, price = ?
                WHERE id = ?
                """, (
                    form.title.data,
                    form.description.data,
                    float(form.price.data),
                    item_id
                )
            )
            conn.commit()

            flash(f"Item {item['title']} has been successfully updated.", "success")
            return redirect(url_for("item", item_id=item_id))

        form.title.data = item["title"]
        form.description.data = item["description"]
        form.price.data = item["price"]

        if form.errors:
            flash(f"{ format.errors }", "danger")

        return render_template("edit_item.html", item=item, form=form)

    return redirect(url_for("home"))


@app.route("/item/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    conn = get_db()
    c = conn.cursor()

    item_from_db = c.execute("SELECT i.id, i.title FROM items AS i WHERE id = ?", (item_id, ))
    row = c.fetchone()

    try:
        item = {
            "id": row[0],
            "title": row[1]
        }
    except:
        item = {}

    if item:
        c.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()

        flash(f"Item {item['title']} has been successfully deleted.", "success")
    else:
        flash("This item does not exist.", "danger")

    return redirect(url_for("home"))


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

    c.execute("""SELECT id, name FROM subcategories WHERE category_id = ?""", (1,))
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
