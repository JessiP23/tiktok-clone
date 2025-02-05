import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import FeatureHasher
import tensorflow as tf

# Load the YouTube Trending dataset
interactions = pd.read_csv('data/youtube-new/USvideos.csv')

# Since the dataset doesn't contain user_id/item_id, use available columns:
# Use "category_id" as a proxy for user_id and "video_id" as item_id.
# Also, use "views" as the rating.
X = interactions[['category_id', 'video_id']]
y = interactions['views']

# For scaling, we'll only use the numeric proxy "category_id"
# (video_id is a string identifier and is not scaled)
X_numeric = interactions[['category_id']]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_numeric, y, test_size=0.2, random_state=42)

# Normalize the training data using StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train a CF model using matrix factorization (NMF) on the scaled category_id values
nmf = NMF(n_components=10, random_state=42)
nmf.fit(X_train_scaled)

# Train a CBF model using item attributes. Here we use the "title" as item attributes.
hasher = FeatureHasher(n_features=100, input_type='string')
item_attributes = hasher.fit_transform(interactions['title'].astype(str))

# Optional: Train a simple TensorFlow model (for regression on ratings)
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(10, input_shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train_scaled, y_train, epochs=10, batch_size=32)

# Create a custom hybrid model combining CF and CBF
class HybridModel:
    def __init__(self, cf_model, cbf_model):
        self.cf_model = cf_model
        self.cbf_model = cbf_model

    def predict(self, user_values):
        # Use the CF model to get latent features
        cf_recommendations = self.cf_model.transform(user_values)
        
        # For the CBF model, simulate predictions using item attributes.
        # Here we use the first item's feature vector as a dummy example.
        cbf_recommendations = np.array(item_attributes.todense())[0]  
        
        # Combine CF and CBF recommendations.
        # This naive example returns a list of latent features from the CF model
        # that match the dummy CBF features.
        hybrid_recommendations = [val for val in cf_recommendations.flatten() if val in cbf_recommendations]
        return hybrid_recommendations

# Create an instance of the hybrid model
hybrid_model = HybridModel(nmf, hasher)

# Use the hybrid model to make predictions using the scaled "category_id" values
hybrid_predictions = hybrid_model.predict(X_test_scaled)
print("Hybrid predictions:", hybrid_predictions)