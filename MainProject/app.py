from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
from collections import Counter
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import csv
import data_analysis
import re
import numpy as np
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
app = Flask(__name__)

def fetch_reviews(product_url):
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    reviews = []
    review_limit=100
    product_name = "product"

    try:
        driver.get(product_url)
        time.sleep(2)

        product_name = driver.title.split(':')[0].strip()  # Extract product name from page title
        product_name = re.sub(r'[\\/*?:"<>|]', '_', product_name)
        while len(reviews) < review_limit:
            review_elements = driver.find_elements(By.XPATH, '//div[@data-hook="review"]')
            for element in review_elements:
                title = element.find_element(By.CSS_SELECTOR, 'a[data-hook="review-title"]').text.strip()
                star_rating = element.find_element(By.CSS_SELECTOR, 'i[data-hook="review-star-rating"]').text.strip()
                review_text = element.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text.strip()
                reviews.append({
                    'title': title,
                    'star_rating': star_rating,
                    'review_text': review_text
                })
                if len(reviews) >= review_limit:
                    break
            try:
                next_button = driver.find_element(By.XPATH, '//a[contains(@class, "a-pagination") and contains(@class, "a-last")]')
                ActionChains(driver).move_to_element(next_button).perform()  # Scrolls to the element
                next_button.click()
            except NoSuchElementException:
                print("Pagination button not found.")
            time.sleep(2)
    finally:
        driver.quit()
    return reviews,product_name


def save_reviews_to_csv(reviews, product_name):
    fieldnames = ['title', 'star_rating', 'review_text']
    csv_path = f'static/{product_name}.csv'  # Save the CSV with the product name
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for review in reviews:
            writer.writerow(review)
    return csv_path  # Return the path to the saved CSV file

def analyze_reviews(reviews):
    sentiments = [review['review_text'] for review in reviews]
    sentiment_counts = Counter('positive' if 'good' in text or 'excellent' in text else 'negative' for text in sentiments)
    return sentiment_counts

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_url = request.form['product_url']
        return redirect(url_for('results', url=product_url))
        reviews, product_name = fetch_reviews(product_url)
        if reviews:
            csv_file_path = os.path.join('uploads', f"{product_name}.csv")
            save_reviews_to_csv(reviews, csv_file_path)
            # Redirect to the analysis page
            return redirect(url_for('analyze', file_name=f"{product_name}.csv"))
    return render_template('home.html')

@app.route('/results')
def results():
    url = request.args.get('url')
    reviews,product_name = fetch_reviews(url)
    if reviews:
        sentiments = analyze_reviews(reviews)
        generate_graphs(reviews)
        csv_path = save_reviews_to_csv(reviews, product_name)
        return render_template('results.html', star_image='/static/star_ratings.png', sentiment_image='/static/sentiments.png', reviews=reviews, sentiments=sentiments)
        return render_template('results.html', reviews=reviews, csv_path=csv_path)
    else:
        return "No reviews or data available."

def generate_graphs(reviews):
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    star_ratings = [review['star_rating'] for review in reviews]
    star_count = Counter(star_ratings)
    stars, counts = zip(*sorted(star_count.items()))
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']

    plt.figure(figsize=(10, 5))
    bars = plt.bar(stars, counts, color=colors)
    plt.xlabel('Star Ratings')
    plt.ylabel('Count')
    plt.title('Star Ratings Distribution')

    total_reviews = sum(counts)
    for bar, count in zip(bars, counts):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{count/total_reviews*100:.1f}%', ha='center', va='bottom', fontsize=9, color='black')

    plt.savefig('static/star_ratings.png')
    plt.close()

    sentiments = [review['review_text'] for review in reviews]
    sentiment_counts = Counter('positive' if 'good' in text or 'excellent' in text else 'negative' for text in sentiments)
    sentiment_labels, sentiment_values = zip(*sentiment_counts.items())
    sentiment_colors = ['green', 'red']

    plt.figure(figsize=(10, 5))
    sentiment_bars = plt.bar(sentiment_labels, sentiment_values, color=sentiment_colors)
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Review Sentiment Analysis')

    for bar, value in zip(sentiment_bars, sentiment_values):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{value/total_reviews*100:.1f}%', ha='center', va='bottom', fontsize=9, color='black')

    plt.savefig('static/sentiments.png')
    plt.close()

@app.route('/analyze')
def analyze():
    # Route to analyze the CSV file and display graphs
    file_name = request.args.get('file_name')
    file_path = os.path.join('uploads', file_name)

    data = data_analysis.load_csv(file_path)  # Load the CSV data
    star_counts = data_analysis.analyze_star_ratings(data)
    sentiment_counts = data_analysis.analyze_sentiments(data)

    # Generate plots
    data_analysis.generate_star_distribution_plot(star_counts)
    data_analysis.generate_sentiment_plot(sentiment_counts)
    data_analysis.generate_word_cloud(data, 'positive')
    data_analysis.generate_word_cloud(data, 'negative')

    return render_template('analyze.html')


if __name__ == '__main__':
    app.run(debug=True)
