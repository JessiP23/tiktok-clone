import logging
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load dataset
interactions = pd.read_csv('../USvideos.csv')
videos = interactions[['video_id', 'title', 'views', 'category_id']].copy()

# Normalize views
scaler = MinMaxScaler()
videos['views_norm'] = scaler.fit_transform(videos[['views']])

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(videos['title'])

def recommend_videos(
    query: str,
    alpha: float = 0.3,  # Default to more content focus when feedback exists
    top_n: int = 10,
    exclude_ids: list = None,
    liked_ids: list = None,
    disliked_ids: list = None
):
    logger.info(f"Generating recommendations for: '{query}'")
    
    # Exclusion handling
    all_excluded = set(exclude_ids or []).union(set(disliked_ids or []))
    candidates = videos[~videos['video_id'].isin(all_excluded)]
    
    if candidates.empty:
        logger.warning("No candidates available after exclusions")
        return []

    indices = candidates.index.tolist()
    candidate_tfidf = tfidf_matrix[indices]

    # Content similarity calculation
    content_sim = np.zeros(len(candidates))
    
    # Blend query and liked similarities
    if liked_ids:
        liked_mask = videos['video_id'].isin(liked_ids)
        if liked_mask.any():
            # Calculate liked similarity
            liked_tfidf = tfidf_matrix[liked_mask]
            liked_vec = liked_tfidf.mean(axis=0)
            liked_sim = cosine_similarity(liked_vec, candidate_tfidf).flatten()
            
            # Calculate query similarity
            query_vec = vectorizer.transform([query])
            query_sim = cosine_similarity(query_vec, candidate_tfidf).flatten()
            
            # Blend with preference for liked content
            content_sim = 0.2 * query_sim + 0.8 * liked_sim
            logger.info("Using blended query + liked similarities")
        else:
            query_vec = vectorizer.transform([query])
            content_sim = cosine_similarity(query_vec, candidate_tfidf).flatten()
    else:
        query_vec = vectorizer.transform([query])
        content_sim = cosine_similarity(query_vec, candidate_tfidf).flatten()

    # Apply disliked penalty
    if disliked_ids:
        disliked_mask = videos['video_id'].isin(disliked_ids)
        if disliked_mask.any():
            disliked_tfidf = tfidf_matrix[disliked_mask]
            disliked_vec = disliked_tfidf.mean(axis=0)
            disliked_sim = cosine_similarity(disliked_vec, candidate_tfidf).flatten()
            
            # Apply dynamic penalty based on number of dislikes
            beta = 1.0 + 0.1 * len(disliked_ids)
            content_sim -= beta * disliked_sim
            logger.info(f"Applied disliked penalty (beta={beta:.2f})")

    # Normalize scores
    content_sim = (content_sim - content_sim.min()) / (content_sim.max() - content_sim.min() + 1e-8)
    cf_scores = candidates['views_norm'].values
    final_scores = alpha * cf_scores + (1 - alpha) * content_sim

    # Generate results
    candidates = candidates.copy()
    candidates['final_score'] = final_scores
    recommendations = (
        candidates.sort_values('final_score', ascending=False)
        .head(top_n)
        .to_dict(orient='records')
    )
    
    logger.debug(f"Top recommendations:\n{pd.DataFrame(recommendations)}")
    return recommendations

@app.route("/recommendations", methods=["GET"])
def recommendations_endpoint():
    params = request.args.to_dict()
    logger.info(f"Request received: {params}")
    
    try:
        recommendations = recommend_videos(
            query=params.get("query", ""),
            alpha=float(params.get("alpha", 0.3)),
            top_n=int(params.get("top_n", 10)),
            exclude_ids=params.get("played", "").split(",") if params.get("played") else None,
            liked_ids=params.get("liked", "").split(",") if params.get("liked") else None,
            disliked_ids=params.get("disliked", "").split(",") if params.get("disliked") else None
        )
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)