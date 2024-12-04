from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import mysql.connector
import os
import logging
from queries import get_sales_for_graph, get_top_returned_skus, search_products
from functools import wraps
import csv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        selected_table = request.form['table']

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Query to fetch all data from the selected table
        query = f"SELECT * FROM {selected_table}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column headers
        headers = [i[0] for i in cursor.description]

        cursor.close()
        conn.close()

        # Create CSV file
        csv_file_path = f'/tmp/{selected_table}_export.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            csvwriter.writerows(rows)

        # Send the file to the user
        return send_file(csv_file_path, as_attachment=True)

    return render_template('export.html')


# Helper function to parse date and extract month and year
def parse_date(date_str):
    try:
        logging.debug(f"Parsing date string: {date_str}")
        # Manually split the date string to handle two-digit years
        day, month_abbr, year_suffix = date_str.strip().split('-')
        month = datetime.strptime(month_abbr, "%b").strftime("%B")
        year = int(year_suffix)
        if year < 100:  # Handle two-digit years
            year += 2000
        return month, year
    except ValueError as e:
        logging.error(f"Error parsing date: {e}")
        raise

# Helper function to parse purchase_date and extract month and year
def parse_purchase_date(date_str):
    try:
        logging.debug(f"Parsing purchase date string: {date_str}")
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        month = date_obj.strftime("%B")
        year = date_obj.year
        return month, year
    except ValueError as e:
        logging.error(f"Error parsing purchase date: {e}")
        raise

# Helper function to convert and handle blank values for numeric fields
def convert_to_float(value):
    try:
        return float(value.strip()) if value.strip() != '' else 0.0
    except ValueError:
        logging.error(f"Invalid numeric value: {value}")
        return None

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

        # Validate and process the TSV file for the returns table
        if selected_table == 'returns':
            with open(file_path, newline='', encoding='latin-1') as tsvfile:
                reader = csv.DictReader(tsvfile, delimiter='\t')
                expected_headers = set(reader.fieldnames)
                required_headers = {
                    'Order ID', 'Order date', 'Return request date', 'Return request status',
                    'Amazon RMA ID', 'Merchant RMA ID', 'Label type', 'Label cost',
                    'Currency code', 'Return carrier', 'Tracking ID', 'Label to be paid by',
                    'A-to-Z Claim', 'Is prime', 'ASIN', 'Merchant SKU', 'Item Name',
                    'Return quantity', 'Return Reason', 'In policy', 'Return type',
                    'Resolution', 'Invoice number', 'Return delivery date', 'Order Amount',
                    'Order quantity', 'SafeT Action reason', 'SafeT claim id', 'SafeT claim state',
                    'SafeT claim creation time', 'SafeT claim reimbursement amount', 'Refunded Amount'
                }

                # Check if headers match
                if not required_headers.issubset(expected_headers):
                    flash('File headers do not match the expected headers.')
                    return redirect(url_for('upload_file'))

                # Prepare data for insertion
                data_to_insert = []
                for row in reader:
                    month, year = parse_date(row['Return request date'])
                    # Prepare the row for insertion, excluding headers
                    data = {
                        'Order ID': row['Order ID'],
                        'Order date': row['Order date'],
                        'Return request date': row['Return request date'],
                        'Return request status': row['Return request status'],
                        'Amazon RMA ID': row['Amazon RMA ID'],
                        'Merchant RMA ID': row['Merchant RMA ID'],
                        'Label type': row['Label type'],
                        'Label cost': row['Label cost'],
                        'Currency code': row['Currency code'],
                        'Return carrier': row['Return carrier'],
                        'Tracking ID': row['Tracking ID'],
                        'Label to be paid by': row['Label to be paid by'],
                        'A-to-Z Claim': row['A-to-Z Claim'],
                        'Is prime': row['Is prime'],
                        'ASIN': row['ASIN'],
                        'Merchant SKU': row['Merchant SKU'],
                        'Item Name': row['Item Name'],
                        'Return quantity': int(row['Return quantity']),
                        'Return Reason': row['Return Reason'],
                        'In policy': row['In policy'],
                        'Return type': row['Return type'],
                        'Resolution': row['Resolution'],
                        'Invoice number': row['Invoice number'],
                        'Return delivery date': row['Return delivery date'],
                        'Order Amount': row['Order Amount'],
                        'Order quantity': int(row['Order quantity']),
                        'SafeT Action reason': row['SafeT Action reason'],
                        'SafeT claim id': row['SafeT claim id'],
                        'SafeT claim state': row['SafeT claim state'],
                        'SafeT claim creation time': row['SafeT claim creation time'],
                        'SafeT claim reimbursement amount': row['SafeT claim reimbursement amount'],
                        'Refunded Amount': row['Refunded Amount'],
                        'month': month,
                        'year': year,
                        'last_updated': datetime.now()
                    }
                    data_to_insert.append(data)

                # Insert data into the returns table
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT INTO returns (
                        `Order ID`, `Order date`, `Return request date`, `Return request status`,
                        `Amazon RMA ID`, `Merchant RMA ID`, `Label type`, `Label cost`,
                        `Currency code`, `Return carrier`, `Tracking ID`, `Label to be paid by`,
                        `A-to-Z Claim`, `Is prime`, `ASIN`, `Merchant SKU`, `Item Name`,
                        `Return quantity`, `Return Reason`, `In policy`, `Return type`,
                        `Resolution`, `Invoice number`, `Return delivery date`, `Order Amount`,
                        `Order quantity`, `SafeT Action reason`, `SafeT claim id`, `SafeT claim state`,
                        `SafeT claim creation time`, `SafeT claim reimbursement amount`, `Refunded Amount`,
                        `month`, `year`, `last_updated`
                    ) VALUES (
                        %(Order ID)s, %(Order date)s, %(Return request date)s, %(Return request status)s,
                        %(Amazon RMA ID)s, %(Merchant RMA ID)s, %(Label type)s, %(Label cost)s,
                        %(Currency code)s, %(Return carrier)s, %(Tracking ID)s, %(Label to be paid by)s,
                        %(A-to-Z Claim)s, %(Is prime)s, %(ASIN)s, %(Merchant SKU)s, %(Item Name)s,
                        %(Return quantity)s, %(Return Reason)s, %(In policy)s, %(Return type)s,
                        %(Resolution)s, %(Invoice number)s, %(Return delivery date)s, %(Order Amount)s,
                        %(Order quantity)s, %(SafeT Action reason)s, %(SafeT claim id)s, %(SafeT claim state)s,
                        %(SafeT claim creation time)s, %(SafeT claim reimbursement amount)s, %(Refunded Amount)s,
                        %(month)s, %(year)s, %(last_updated)s
                    )
                """, data_to_insert)
                conn.commit()
                cursor.close()
                conn.close()

                flash('File uploaded and processed successfully!')
                return redirect(url_for('upload_file'))

        # Add logic to handle sales table upload
        elif selected_table == 'sales':
            with open(file_path, newline='', encoding='latin-1') as txtfile:
                reader = csv.DictReader(txtfile, delimiter='\t')
                expected_headers = set(reader.fieldnames)
                # Map file headers to database fields
                header_map = {
                    'amazon-order-id': 'amazon_order_id',
                    'merchant-order-id': 'merchant_order_id',
                    'purchase-date': 'purchase_date',
                    'last-updated-date': 'last_updated_date',
                    'order-status': 'order_status',
                    'fulfillment-channel': 'fulfillment_channel',
                    'sales-channel': 'sales_channel',
                    'order-channel': 'order_channel',
                    'url': 'url',
                    'ship-service-level': 'ship_service_level',
                    'product-name': 'product_name',
                    'sku': 'sku',
                    'asin': 'asin',
                    'number-of-items': 'number_of_items',
                    'item-status': 'item_status',
                    'tax-collection-model': 'tax_collection_model',
                    'tax-collection-responsible-party': 'tax_collection_responsible_party',
                    'quantity': 'quantity',
                    'currency': 'currency',
                    'item-price': 'item_price',
                    'item-tax': 'item_tax',
                    'shipping-price': 'shipping_price',
                    'shipping-tax': 'shipping_tax',
                    'gift-wrap-price': 'gift_wrap_price',
                    'gift-wrap-tax': 'gift_wrap_tax',
                    'item-promotion-discount': 'item_promotion_discount',
                    'ship-promotion-discount': 'ship_promotion_discount',
                    'ship-city': 'ship_city',
                    'ship-state': 'ship_state',
                    'ship-postal-code': 'ship_postal_code',
                    'ship-country': 'ship_country',
                    'promotion-ids': 'promotion_ids',
                    'payment-method-details': 'payment_method_details',
                    'is-business-order': 'is_business_order',
                    'purchase-order-number': 'purchase_order_number',
                    'price-designation': 'price_designation',
                    'customized-url': 'customized_url',
                    'customized-page': 'customized_page',
                    'signature-confirmation-recommended': 'signature_confirmation_recommended'
                }
                # Trim whitespace from expected headers
                expected_headers = {h.strip() for h in expected_headers}
                # Trim whitespace from header_map keys
                header_map = {k.strip(): v for k, v in header_map.items()}
                # Convert file headers to database fields
                converted_headers = {header_map.get(h, h) for h in expected_headers}
                required_headers = set(header_map.values())

                # Debugging: Print headers for comparison
                logging.debug(f"Expected Headers: {expected_headers}")
                logging.debug(f"Converted Headers: {converted_headers}")
                logging.debug(f"Required Headers: {required_headers}")

                # Check if headers match
                if not required_headers.issubset(converted_headers):
                    flash('File headers do not match the expected headers.')
                    return redirect(url_for('upload_file'))

                # Prepare data for insertion
                data_to_insert = []
                for row in reader:
                    # Convert and handle blank values for numeric fields
                    row['number-of-items'] = convert_to_float(row['number-of-items'])
                    row['item-tax'] = convert_to_float(row['item-tax'])
                    row['shipping-price'] = convert_to_float(row['shipping-price'])
                    row['shipping-tax'] = convert_to_float(row['shipping-tax'])
                    row['gift-wrap-price'] = convert_to_float(row['gift-wrap-price'])
                    row['gift-wrap-tax'] = convert_to_float(row['gift-wrap-tax'])
                    row['item-promotion-discount'] = convert_to_float(row['item-promotion-discount'])
                    row['ship-promotion-discount'] = convert_to_float(row['ship-promotion-discount'])
                    row['item-price'] = convert_to_float(row['item-price'])
                    row['is-business-order'] = 1 if row['is-business-order'].lower() == 'true' else 0

                    # Trim whitespace from row keys
                    row = {k.strip(): v for k, v in row.items()}
                    month, year = parse_purchase_date(row['purchase-date'])
                    # Prepare the row for insertion, excluding headers
                    data = {header_map[k]: v for k, v in row.items()}
                    data.update({'month': month, 'year': year, 'last_updated': datetime.now()})
                    if 'signature_confirmation_recommended' in data:
                        data['signature_confirmation_recommended'] = 1 if data['signature_confirmation_recommended'].lower() == 'true' else 0
                    data_to_insert.append(data)

                # Insert data into the sales table
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT INTO sales (
                        `amazon_order_id`, `merchant_order_id`, `purchase_date`, `last_updated_date`,
                        `order_status`, `fulfillment_channel`, `sales_channel`, `order_channel`, `url`,
                        `ship_service_level`, `product_name`, `sku`, `asin`, `number_of_items`, `item_status`,
                        `tax_collection_model`, `tax_collection_responsible_party`, `quantity`, `currency`,
                        `item_price`, `item_tax`, `shipping_price`, `shipping_tax`, `gift_wrap_price`,
                        `gift_wrap_tax`, `item_promotion_discount`, `ship_promotion_discount`, `ship_city`,
                        `ship_state`, `ship_postal_code`, `ship_country`, `promotion_ids`,
                        `payment_method_details`, `is_business_order`, `purchase_order_number`,
                        `price_designation`, `customized_url`, `customized_page`,
                        `signature_confirmation_recommended`, `month`, `year`, `last_updated`
                    ) VALUES (
                        %(amazon_order_id)s, %(merchant_order_id)s, %(purchase_date)s, %(last_updated_date)s,
                        %(order_status)s, %(fulfillment_channel)s, %(sales_channel)s, %(order_channel)s, %(url)s,
                        %(ship_service_level)s, %(product_name)s, %(sku)s, %(asin)s, %(number_of_items)s, %(item_status)s,
                        %(tax_collection_model)s, %(tax_collection_responsible_party)s, %(quantity)s, %(currency)s,
                        %(item_price)s, %(item_tax)s, %(shipping_price)s, %(shipping_tax)s, %(gift_wrap_price)s,
                        %(gift_wrap_tax)s, %(item_promotion_discount)s, %(ship_promotion_discount)s, %(ship_city)s,
                        %(ship_state)s, %(ship_postal_code)s, %(ship_country)s, %(promotion_ids)s,
                        %(payment_method_details)s, %(is_business_order)s, %(purchase_order_number)s,
                        %(price_designation)s, %(customized_url)s, %(customized_page)s,
                        %(signature_confirmation_recommended)s, %(month)s, %(year)s, %(last_updated)s
                    )
                """, data_to_insert)
                conn.commit()
                cursor.close()
                conn.close()

                flash('File uploaded and processed successfully!', 'success')
                return redirect(url_for('upload_file'))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)