# Amazon Seller Central Returns Reports App

This is a simple web application that allows you to upload TSV files containing Amazon returns data and export reports in a user-friendly format. The app is built using Python, Flask, and MySQL. 

As of now, there is no API integration. You'll need to export the reports from seller central and upload them to the app.

# Installation

1. Clone the repository: `git clone https://github.com/bcm082/amzreturns.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

# MySQL Database

The application uses a MySQL database to store the returns data. The database files are in the Db_Schema directory. There are three tables:

- `returns`: Contains the returns data for each product.
- `sales`: Contains the sales data for each product.
- `users`: Contains user information, including email and password.

# Usage

1. Navigate to seller central reports and click on Returns Reports. Select the date range (one month at the time is better) and download the report as a TSV file.
2. In seller central, click on reports again, and then click Fullfillment Reports. Click on All Orders, and select the date range and download the repor and download.
3. In the web app go to the localhost/upload page and upload the returns and sales files to their respective tables. Make you create a user in the users table to log in to the app.
4. Once the files are uploaded, you can view the reports in the products page. You can also export the reports to a CSV file.

# License

This project is licensed under the MIT License.



