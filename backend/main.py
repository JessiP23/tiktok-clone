import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the YouTube Trending dataset
interactions = pd.read_csv('/kaggle/working/data/youtube-new/USvideos.csv')

# Select relevant columns
videos = interactions[['video_id', 'title', 'views', 'category_id']].copy()

# ---------------------------
# CF Component (Popularity Proxy)
# ---------------------------
# Use "views" as a proxy for rating.
# Normalize the views so that higher view counts give a higher CF score.
scaler = MinMaxScaler()
videos['views_norm'] = scaler.fit_transform(videos[['views']])

# ---------------------------
# CBF Component (Content similarity)
# ---------------------------
# Use TF-IDF on the video titles
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(videos['title'])

# ---------------------------
# Hybrid Recommendation Function
# ---------------------------
def recommend_videos(query, alpha=0.5, top_n=10):
    """
    Recommend videos based on a query string.

    Parameters:
      query (str): Query text (can be a video title or keyword).
      alpha (float): Weight for the CF score (normalized views). The content-based 
                     similarity receives weight (1 - alpha).
      top_n (int): Number of top recommendations to return.
    
    Returns:
      DataFrame containing video_id, title, and final hybrid score.
    """
    # Compute TF-IDF vector for the query
    query_vec = vectorizer.transform([query])
    # Compute cosine similarity between query and all video titles
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    # Normalize the similarity scores to [0, 1]
    sim_norm = (sim_scores - sim_scores.min()) / (sim_scores.max() - sim_scores.min() + 1e-8)
    
    # Get the CF score from normalized views
    cf_scores = videos['views_norm'].values
    # Compute the final hybrid score as a weighted combination
    final_scores = alpha * cf_scores + (1 - alpha) * sim_norm
    
    # Attach scores to the dataframe and sort by the final score descending
    videos['final_score'] = final_scores
    recommended = videos.sort_values(by='final_score', ascending=False).head(top_n)
    return recommended[['video_id', 'title', 'final_score']]

# ---------------------------
# Example Usage
# ---------------------------
# For demonstration, use the title of the first video in the dataset as the query.
sample_query = videos['title'].iloc[0]
recommendations = recommend_videos(sample_query, alpha=0.5, top_n=10)

print("Recommendations:")
print(recommendations)