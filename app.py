from flask import Flask, render_template, request, redirect, session, url_for
from db import db, cursor
import requests

app = Flask(__name__)
app.secret_key = "secret123"

def fetch_dummyjson_products(product_name):
    try:
        url = f"https://dummyjson.com/products/search?q={product_name}"
        response = requests.get(url, timeout=10)
        data = response.json()

        results = []

        for item in data.get("products", [])[:3]:
            base_price = float(item.get("price", 0))
            title = item.get("title", "No Title")
            category = item.get("category", "Unknown")

            results.append({
                "website": "Amazon",
                "title": f"{title} ({category})",
                "price": round(base_price + 20, 2),
                "link": "https://www.amazon.in"
            })

            results.append({
                "website": "Flipkart",
                "title": f"{title} ({category})",
                "price": round(base_price - 10, 2),
                "link": "https://www.flipkart.com"
            })

            results.append({
                "website": "Croma",
                "title": f"{title} ({category})",
                "price": round(base_price + 5, 2),
                "link": "https://www.croma.com"
            })

        print("API results:", results)
        return results

    except Exception as e:
        print("API fetch error:", e)
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    product_name = request.form['product_name']

    cursor.execute("INSERT INTO search_history (search_name) VALUES (%s)", (product_name,))
    db.commit()
    search_id = cursor.lastrowid

    cursor.execute("""
    SELECT website_name, product_name, price, product_link, image_url, rating, reviews_count
    FROM product_catalog
    WHERE product_name LIKE %s OR category LIKE %s
""", (f"%{product_name}%", f"%{product_name}%"))

    rows = cursor.fetchall()

    results = []
    for row in rows:
         product_title = row["product_name"]
         website = row["website_name"]

         if website == "Amazon":
              product_link = f"https://www.amazon.in/s?k={product_title.replace(' ', '+')}"
         elif website == "Flipkart":
              product_link = f"https://www.flipkart.com/search?q={product_title.replace(' ', '%20')}"
         elif website == "Croma":
              product_link = f"https://www.croma.com/searchB?q={product_title.replace(' ', '%20')}:relevance"
         else:
              product_link = row["product_link"]

         results.append({
             "website": row["website_name"],
             "title": row["product_name"],
             "price": float(row["price"]),
              "link": product_link,
             "image": row["image_url"] if row["image_url"] else "https://via.placeholder.com/300x200?text=No+Image",
             "rating": row["rating"] if row["rating"] is not None else 4.3,
             "reviews": row["reviews_count"] if row["reviews_count"] is not None else 150
})


    for item in results:
        cursor.execute("""
            INSERT INTO compared_products (search_id, website_name, product_title, price, product_link)
            VALUES (%s, %s, %s, %s, %s)
        """, (search_id, item['website'], item['title'], item['price'], item['link']))
        db.commit()

    results = sorted(results, key=lambda x: x['price'])

    return render_template('results.html', results=results, product_name=product_name)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()

        if admin:
            session['admin'] = admin['username']
            return redirect('/admin/dashboard')
        else:
            return "Invalid login"

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin/login')

    cursor.execute("""
        SELECT 
            cp.id,
            cp.search_id,
            cp.website_name,
            cp.product_title,
            cp.price,
            cp.product_link,
            cp.fetched_at,
            pc.category,
            pc.image_url,
            pc.rating,
            pc.reviews_count
        FROM compared_products cp
        LEFT JOIN product_catalog pc
            ON cp.product_title = pc.product_name
            AND cp.website_name = pc.website_name
        ORDER BY cp.fetched_at DESC
    """)
    products = cursor.fetchall()

    return render_template('admin_dashboard.html', products=products)
@app.route('/admin/search-history')
def admin_search_history():
    if 'admin' not in session:
        return redirect('/admin/login')

    cursor.execute("SELECT * FROM search_history ORDER BY id DESC")
    searches = cursor.fetchall()

    return render_template('search_history.html', searches=searches)
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')

if __name__ == '__main__':
    app.run(debug=True)