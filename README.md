# Learning Flask - Web Forms

Based on this course: _[Creating and Processing Web Forms with Flask](https://app.pluralsight.com/library/courses/creating-processing-web-forms-flask/table-of-contents)_.

To create virtual environment run:

_Linux_

```
python -m venv venv
./venv/Scripts/activate
```

_Windows_

```
python -m venv venv
.\venv\Scripts\activate
```

To save requirements run:
```
pip freeze > requirements.txt
```

To install requirements run:

```
pip install -r requirements.txt
```

To start Flask application do this:

_Linux_

```
export FLASK_APP=globomatics_shop.py
export FLASK_ENV=development
flask run
```

_Windows_ (Command Line)

```
set FLASK_APP=globomatics_shop.py
set FLASK_ENV=development
flask run
```

_Windows_ (PowerShell)

```
$Env:FLASK_APP='globomatics_shop.py'
$Env:FLASK_ENV='development'
flask run
```