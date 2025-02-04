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
