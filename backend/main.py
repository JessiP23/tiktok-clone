import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score

# load the interaction matrix and split it into training and testing sets
interactions = pd.read_csv('data/interactions.csv')
user_id, item_id, rating = interactions['user_id'], interactions['item_id'], interactions['rating']

# split the interaction matrix into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(user_id, item_id, rating, test_size=0.2, random_state=42)


# Normalize the interaction matrix using StandardScaler
scaler = StandardScaler()

# Fit and transfer the interaction matrix
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# train a cf model using matrix factorization
from sklearn.decomposition import NMF

# create a NMF instance with 10 latent factors
nmf = NMF(n_components=10, random_state=42)

# Fit the model to the scaled interaction matrix
nmf.fit(X_train_scaled)

