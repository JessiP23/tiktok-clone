import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the YouTube Trending dataset
interactions = pd.read_csv('../USvideos.csv')

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
def recommend_videos(query: str, alpha: float=0.5, top_n: int=10, exclude_ids: list=None):
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
    
    if not query:
      query = videos['title'].iloc[0]

    # Compute TF-IDF vector for the query
    if exclude_ids:
        df_filtered = videos[~videos['video_id'].isin(exclude_ids)].copy()
        if df_filtered.empty:
            # If all videos were excluded, revert to full dataset.
            df_filtered = videos.copy()
        indices = df_filtered.index.tolist()
        filtered_tfidf = tfidf_matrix[indices]
        # Compute similarity using filtered tweets.
        query_vec = vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, filtered_tfidf).flatten()
        sim_norm = (sim_scores - sim_scores.min()) / (sim_scores.max() - sim_scores.min() + 1e-8)
        cf_scores = df_filtered['views_norm'].values
        final_scores = alpha * cf_scores + (1 - alpha) * sim_norm
        df_filtered['final_score'] = final_scores
        recommended = df_filtered.sort_values(by='final_score', ascending=False).head(top_n)
        return recommended[['video_id', 'title', 'final_score']].to_dict(orient='records')
    else:
        # No exclusion: use the full dataset.
        query_vec = vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        sim_norm = (sim_scores - sim_scores.min()) / (sim_scores.max() - sim_scores.min() + 1e-8)
        cf_scores = videos['views_norm'].values
        final_scores = alpha * cf_scores + (1 - alpha) * sim_norm
        videos['final_score'] = final_scores
        recommended = videos.sort_values(by='final_score', ascending=False).head(top_n)
        return recommended[['video_id', 'title', 'final_score']].to_dict(orient='records')

@app.route("/recommendations", methods=["GET"])
def recommendations_endpoint():
    query = request.args.get("query", default="", type=str)
    alpha = request.args.get("alpha", default=0.5, type=float)
    top_n = request.args.get("top_n", default=10, type=int)
    # Exclude played videos (comma separated video_ids)
    played_str = request.args.get("played", default="", type=str)
    exclude_ids = [vid for vid in played_str.split(",") if vid] if played_str else None
    
    try:
        recs = recommend_videos(query, alpha=alpha, top_n=top_n, exclude_ids=exclude_ids)
        return jsonify(recs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# Sample usage (for local testing)
# ---------------------------
if __name__ == '__main__':
    # Run Flask without the reloader to prevent issues in some IDEs.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)