from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from queries import get_sales_for_graph, get_top_returned_skus, search_products
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'returns_db'
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Root route
@app.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to check if the user exists
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch data for the graph
    sales_graph_data = get_sales_for_graph()
    top_returned_skus = get_top_returned_skus()

    return render_template(
        'dashboard.html',
        username=session['email'],
        sales_graph_data=sales_graph_data,
        top_returned_skus=top_returned_skus
    )

# Route for Products
@app.route('/products', methods=['GET', 'POST'])
def products():
    search_results = {'summary': None, 'products': []}
    search_term = request.form.get('search_term', '').strip()  # Get search term from the form

    if search_term:  # Only query if there's a search term
        search_results = search_products(search_term)

    return render_template(
        'products.html',
        search_term=search_term,
        summary=search_results['summary'],
        products=search_results['products']
    )


# Route for Export
@app.route('/export')
def export():
    # Logic for exporting data can be implemented here
    return render_template('export.html')


# Route for Upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # Get the uploaded file and selected table
        uploaded_file = request.files['file']
        selected_table = request.form['table']

        # Check if a file is uploaded
        if uploaded_file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        # Save the file to a temporary location
        file_path = os.path.join('/tmp', uploaded_file.filename)
        uploaded_file.save(file_path)

        # Here you would add the logic to validate the file headers and upload to the database
        # For now, let's just flash a success message
        flash(f'File uploaded successfully to {selected_table} table!')
        return redirect(url_for('upload_file'))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)