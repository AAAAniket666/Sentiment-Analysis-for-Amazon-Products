def analyze_reviews(reviews_list):
    # Example sentiment analysis function that just counts positives and negatives
    sentiment_counts = {'positive': 0, 'negative': 0}
    for review in reviews_list:
        if 'good' in review or 'excellent' in review:
            sentiment_counts['positive'] += 1
        else:
            sentiment_counts['negative'] += 1
    return sentiment_counts

