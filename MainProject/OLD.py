from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
from collections import Counter
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)  # Use __name__ to correctly initialize the Flask app

def fetch_reviews(product_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    reviews = []
    # Update these selectors based on the actual HTML structure of Amazon's product page
    review_elements = soup.find_all('div', {'data-hook': 'review'})  # Commonly used data-hook for reviews on Amazon

    for element in review_elements:
        title = element.find('a', {'data-hook': 'review-title'}).text.strip() if element.find('a', {'data-hook': 'review-title'}) else 'No Title'
        star_rating = element.find('i', {'data-hook': 'review-star-rating'}).text.strip() if element.find('i', {'data-hook': 'review-star-rating'}) else 'No Rating'
        review_text = element.find('span', {'data-hook': 'review-body'}).text.strip() if element.find('span', {'data-hook': 'review-body'}) else 'No Review Text'
        reviews.append({
            'title': title,
            'star_rating': star_rating,
            'review_text': review_text
        })

    print(f"Fetched {len(reviews)} reviews.")
    if reviews:
        return reviews
    else:
        return None
reviews_url = 'https://www.amazon.in/product-reviews/B09G9HD6PD/ref=acr_dp_hist_5?ie=UTF8&filterByStar=five_star&reviewerType=all_reviews#reviews-filter-bar'
reviews = fetch_reviews(reviews_url)
if reviews:
    print(reviews)
else:
    print("No reviews fetched.")


def analyze_reviews(reviews):
    sentiments = [review['review_text'] for review in reviews]
    sentiment_counts = Counter('positive' if 'good' in text or 'excellent' in text else 'negative' for text in sentiments)
    return sentiment_counts

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_url = request.form['product_url']
        return redirect(url_for('results', url=product_url))
    return render_template('home.html')

@app.route('/results')
def results():
    url = request.args.get('url')
    reviews = fetch_reviews(url)
    if reviews:
        sentiments = analyze_reviews(reviews)
        generate_graphs(reviews)
        return render_template('results.html', star_image='/static/star_ratings.png', sentiment_image='/static/sentiments.png', reviews=reviews, sentiments=sentiments)
    else:
        return "No reviews or data available."

def generate_graphs(reviews):
    # Generating star ratings distribution graph
    star_ratings = [review['star_rating'] for review in reviews]
    star_count = Counter(star_ratings)
    plt.figure(figsize=(10, 5))
    plt.bar(star_count.keys(), star_count.values(), color='blue')
    plt.xlabel('Star Ratings')
    plt.ylabel('Count')
    plt.title('Star Ratings Distribution')
    plt.savefig('static/star_ratings.png')
    plt.close()

    sentiments = [analyze_reviews(review['review_text']) for review in reviews]
    sentiment_count = Counter(sentiments)
    plt.figure(figsize=(10, 5))
    plt.bar(sentiment_count.keys(), sentiment_count.values(), color=['green', 'red'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Review Sentiment Analysis')
    plt.savefig('static/sentiments.png')
    plt.close()

if __name__ == '__main__':
    app.run(debug=True)