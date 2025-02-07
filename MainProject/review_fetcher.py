import requests
from bs4 import BeautifulSoup

def fetch_reviews(product_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    reviews = []
    ratings = {}
    
    review_elements = soup.find_all('div', class_='review')  # Example: update this to the correct class or ID
    for element in review_elements:
        title = element.find('a', class_='review-title').text.strip() if element.find('a', class_='review-title') else 'No Title'
        star_rating = element.find('i', class_='review-rating').text.strip() if element.find('i', class_='review-rating') else 'No Rating'
        review_text = element.find('span', class_='review-text').text.strip() if element.find('span', class_='review-text') else 'No Review Text'
        reviews.append({
            'title': title,
            'star_rating': star_rating,
            'review_text': review_text
        })  
    print(reviews)
    print(f"Fetched {len(reviews)} reviews.")
    return reviews, ratings
