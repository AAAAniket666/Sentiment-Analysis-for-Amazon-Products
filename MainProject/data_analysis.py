import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud

def load_csv(file_path):
    # Load data from the CSV file
    data = pd.read_csv(file_path)
    return data

def analyze_star_ratings(data):
    # Count the star ratings
    star_counts = data['star_rating'].value_counts()
    return star_counts

def analyze_sentiments(data):
    # Simple sentiment analysis based on keywords
    positive_keywords = ['good', 'excellent', 'great', 'love']
    data['sentiment'] = data['review_text'].apply(
        lambda text: 'positive' if any(word in text.lower() for word in positive_keywords) else 'negative'
    )
    sentiment_counts = data['sentiment'].value_counts()
    return sentiment_counts

def generate_star_distribution_plot(star_counts):
    # Plot the distribution of star ratings
    plt.figure(figsize=(8, 6))
    star_counts.plot(kind='bar', color='skyblue')
    plt.xlabel('Star Rating')
    plt.ylabel('Count')
    plt.title('Distribution of Star Ratings')
    plt.show()

def generate_sentiment_plot(sentiment_counts):
    # Plot the sentiment analysis results
    plt.figure(figsize=(8, 6))
    sentiment_counts.plot(kind='bar', color=['green', 'red'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis')
    plt.show()

def generate_word_cloud(data, sentiment):
    # Generate a word cloud for a given sentiment
    reviews_text = ' '.join(data[data['sentiment'] == sentiment]['review_text'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud of {sentiment.capitalize()} Reviews')
    plt.show()