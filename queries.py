import mysql.connector

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'returns_db'
}

def get_sales_for_graph():
    """
    Fetch data for the line graph of return quantities by year and month.
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        year AS Year, 
        month AS Month, 
        SUM(`Return quantity`) AS Total_Return_Quantity
    FROM 
        returns
    GROUP BY 
        year, month
    ORDER BY 
        year, month;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Organize data for the graph
    MONTH_NAME_TO_NUMBER = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}
    data = {}
    for row in results:
        year = row['Year']
        month_name = row['Month']  # Get the month name as a string
        month = MONTH_NAME_TO_NUMBER.get(month_name, 0)  # Convert to number, default to 0 if invalid

        if year not in data:
            data[year] = [0] * 12  # Create an empty list for 12 months
        
        if month > 0:  # Ensure month is valid
            data[year][month - 1] = row['Total_Return_Quantity']
    return data

def get_top_returned_skus():
    """
    Fetch the top 50 most returned SKUs from the year 2024, along with their total sales.

    Args:
        db_connection: A MySQL database connection object.

    Returns:
        A list of dictionaries containing SKU, return quantity, and total sold quantity.
    """

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            r.asin AS asin, 
            r.`Merchant SKU` AS merchant_sku,
            r.total_returns, 
            s.total_sold
        FROM 
            (SELECT asin, 
                    `Merchant SKU`, 
                    SUM(`return quantity`) AS total_returns 
            FROM returns 
            WHERE year = 2024 
            GROUP BY asin, `Merchant SKU`) r
        LEFT JOIN 
            (SELECT asin, SUM(quantity) AS total_sold 
            FROM sales 
            WHERE year = 2024 
            GROUP BY asin) s
        ON 
            r.asin = s.asin
        ORDER BY 
            r.total_returns DESC
        LIMIT 50;
        """
# Create a new cursor
    try:
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all results
    finally:
        cursor.close()  # Ensure the cursor is always closed
    return results


def search_products(search_term):
    """
    Search for products by name or SKU and return their return/sales data by year
    including return reasons breakdown
    """
    if not search_term:
        return []

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # First query for main product stats
    main_query = """
    SELECT 
        r.asin,
        GROUP_CONCAT(DISTINCT r.`Merchant SKU`) as merchant_skus,
        -- 2023 data
        SUM(r.returns_2023) as returns_2023,
        COALESCE(s.sales_2023, 0) as sales_2023,
        ROUND(
            (SUM(r.returns_2023) / NULLIF(COALESCE(s.sales_2023, 0), 0)) * 100,
            2
        ) as return_rate_2023,
        -- 2024 data
        SUM(r.returns_2024) as returns_2024,
        COALESCE(s.sales_2024, 0) as sales_2024,
        ROUND(
            (SUM(r.returns_2024) / NULLIF(COALESCE(s.sales_2024, 0), 0)) * 100,
            2
        ) as return_rate_2024
    FROM 
        (SELECT 
            asin,
            `Merchant SKU`,
            SUM(CASE WHEN year = 2023 THEN 1 ELSE 0 END) as returns_2023,
            SUM(CASE WHEN year = 2024 THEN 1 ELSE 0 END) as returns_2024
        FROM returns 
        WHERE 
            `Merchant SKU` LIKE %s 
            OR asin LIKE %s
        GROUP BY asin, `Merchant SKU`) r
    LEFT JOIN 
        (SELECT 
            asin,
            SUM(CASE WHEN year = 2023 THEN quantity ELSE 0 END) as sales_2023,
            SUM(CASE WHEN year = 2024 THEN quantity ELSE 0 END) as sales_2024
        FROM sales
        GROUP BY asin) s
    ON r.asin = s.asin
    GROUP BY 
        r.asin,
        s.sales_2023,
        s.sales_2024
    ORDER BY 
        returns_2024 DESC
    """

    # Second query for return reasons
    reasons_query = """
    SELECT 
        r.asin,
        r.`Return Reason`,
        SUM(CASE WHEN r.year = 2023 THEN 1 ELSE 0 END) as reason_count_2023,
        SUM(CASE WHEN r.year = 2024 THEN 1 ELSE 0 END) as reason_count_2024
    FROM returns r
    WHERE 
        r.`Merchant SKU` LIKE %s 
        OR r.asin LIKE %s
    GROUP BY 
        r.asin,
        r.`Return Reason`
    ORDER BY 
        r.asin,
        SUM(CASE WHEN r.year = 2024 THEN 1 ELSE 0 END) DESC
    """
    
    try:
        search_pattern = f"%{search_term}%"
        
        # Execute main query
        cursor.execute(main_query, (search_pattern, search_pattern))
        products = cursor.fetchall()
        
        # Execute reasons query
        cursor.execute(reasons_query, (search_pattern, search_pattern))
        reasons = cursor.fetchall()
        
        # Group reasons by ASIN
        reasons_by_asin = {}
        for reason in reasons:
            asin = reason['asin']
            if asin not in reasons_by_asin:
                reasons_by_asin[asin] = []
            reasons_by_asin[asin].append({
                'reason': reason['Return Reason'],
                'count_2023': reason['reason_count_2023'],
                'count_2024': reason['reason_count_2024']
            })
        
        # Add reasons to each product
        for product in products:
            product['return_reasons'] = reasons_by_asin.get(product['asin'], [])

        # Calculate summary totals
        summary = {
            'total_returns_2023': sum(p['returns_2023'] for p in products),
            'total_sales_2023': sum(p['sales_2023'] for p in products),
            'total_returns_2024': sum(p['returns_2024'] for p in products),
            'total_sales_2024': sum(p['sales_2024'] for p in products)
        }
        summary['return_rate_2023'] = round((summary['total_returns_2023'] / summary['total_sales_2023']) * 100, 2) if summary['total_sales_2023'] else 0
        summary['return_rate_2024'] = round((summary['total_returns_2024'] / summary['total_sales_2024']) * 100, 2) if summary['total_sales_2024'] else 0

        # Aggregate return reasons
        combined_reasons = {}
        for product in products:
            for reason in product['return_reasons']:
                reason_text = reason['reason']
                if reason_text not in combined_reasons:
                    combined_reasons[reason_text] = {'count_2023': 0, 'count_2024': 0}
                combined_reasons[reason_text]['count_2023'] += reason['count_2023']
                combined_reasons[reason_text]['count_2024'] += reason['count_2024']

        summary['combined_reasons'] = combined_reasons
        
        return {'summary': summary, 'products': products}
    finally:
        cursor.close()
        conn.close()
    
    return products