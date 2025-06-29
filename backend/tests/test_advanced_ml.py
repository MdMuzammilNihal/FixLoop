"""
Test file for advanced machine learning and deep learning capabilities.
This file contains multiple ML/DL techniques and models to test how well the AI assistant
handles ML/DL code and provides effective solutions.
"""
import numpy as np
import pandas as pd
import time
import os
import pickle
from typing import List, Dict, Tuple, Any, Optional, Union

# Try to import sklearn
try:
    from sklearn.datasets import load_iris, load_digits, load_wine, load_breast_cancer
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.decomposition import PCA
    import sklearn
    SKLEARN_AVAILABLE = True
except ImportError:
    print("scikit-learn is not available. Install with: pip install scikit-learn")
    SKLEARN_AVAILABLE = False

# Try to import torch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch is not available. Install with: pip install torch")
    TORCH_AVAILABLE = False

# Try to import tensorflow/keras
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    print("TensorFlow is not available. Install with: pip install tensorflow")
    TF_AVAILABLE = False

# ====== Basic ML Examples ======

def test_basic_classification():
    """Test basic classification with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_basic_classification: scikit-learn not available")
        return
    
    print("Running basic classification test...")
    
    # Load dataset
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Try different classifiers
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=200),
        "Decision Tree": DecisionTreeClassifier(),
        "Random Forest": RandomForestClassifier(),
        "Support Vector Machine": SVC(probability=True),
        "K-Nearest Neighbors": KNeighborsClassifier()
    }
    
    results = {}
    
    for name, clf in classifiers.items():
        # Train model
        start_time = time.time()
        clf.fit(X_train, y_train)
        
        # Make predictions
        y_pred = clf.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        train_time = time.time() - start_time
        
        results[name] = {
            "accuracy": accuracy,
            "train_time": train_time
        }
        
        print(f"{name}: Accuracy = {accuracy:.4f}, Training time = {train_time:.4f}s")
    
    # Export results as CSV
    df = pd.DataFrame.from_dict(results, orient='index')
    df.to_csv('classification_results.csv')
    print("Saved classification results to classification_results.csv")

def test_regression():
    """Test regression algorithms with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_regression: scikit-learn not available")
        return
    
    print("Running regression test...")
    
    # Generate synthetic regression data
    from sklearn.datasets import make_regression
    
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.5, random_state=42)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Try different regression models
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.svm import SVR
    
    regressors = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(),
        "Lasso Regression": Lasso(),
        "ElasticNet": ElasticNet(),
        "Random Forest": RandomForestRegressor(),
        "Gradient Boosting": GradientBoostingRegressor(),
        "Support Vector Regression": SVR()
    }
    
    results = {}
    
    for name, regressor in regressors.items():
        # Train model
        start_time = time.time()
        regressor.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = regressor.predict(X_test_scaled)
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        train_time = time.time() - start_time
        
        results[name] = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "train_time": train_time
        }
        
        print(f"{name}: RMSE = {rmse:.4f}, MAE = {mae:.4f}, R² = {r2:.4f}, Training time = {train_time:.4f}s")
    
    # Export results as CSV
    df = pd.DataFrame.from_dict(results, orient='index')
    df.to_csv('regression_results.csv')
    print("Saved regression results to regression_results.csv")

def test_clustering():
    """Test clustering algorithms with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_clustering: scikit-learn not available")
        return
    
    print("Running clustering test...")
    
    # Generate synthetic clustering data
    from sklearn.datasets import make_blobs
    
    X, y_true = make_blobs(n_samples=500, centers=4, cluster_std=0.6, random_state=42)
    
    # Try different clustering algorithms
    from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
    
    # K-Means
    kmeans = KMeans(n_clusters=4, random_state=42)
    kmeans_labels = kmeans.fit_predict(X)
    
    # Agglomerative Clustering
    agg_clustering = AgglomerativeClustering(n_clusters=4)
    agg_labels = agg_clustering.fit_predict(X)
    
    # DBSCAN
    dbscan = DBSCAN(eps=0.3, min_samples=10)
    dbscan_labels = dbscan.fit_predict(X)
    
    # Evaluate clusters with various metrics
    from sklearn.metrics import silhouette_score, calinski_harabasz_score
    
    # Only compute scores for valid clusterings (more than one cluster)
    scores = {}
    
    if len(set(kmeans_labels)) > 1:
        scores["K-Means"] = {
            "silhouette": silhouette_score(X, kmeans_labels),
            "calinski_harabasz": calinski_harabasz_score(X, kmeans_labels)
        }
    
    if len(set(agg_labels)) > 1:
        scores["Agglomerative"] = {
            "silhouette": silhouette_score(X, agg_labels),
            "calinski_harabasz": calinski_harabasz_score(X, agg_labels)
        }
    
    if len(set(dbscan_labels)) > 1:
        scores["DBSCAN"] = {
            "silhouette": silhouette_score(X, dbscan_labels),
            "calinski_harabasz": calinski_harabasz_score(X, dbscan_labels)
        }
    
    for name, metrics in scores.items():
        print(f"{name}: Silhouette = {metrics['silhouette']:.4f}, Calinski-Harabasz = {metrics['calinski_harabasz']:.4f}")

# ====== NLP Examples ======

def test_nlp_basics():
    """Test basic NLP techniques with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_nlp_basics: scikit-learn not available")
        return
    
    print("Running NLP basics test...")
    
    # Sample text data
    documents = [
        "Machine learning is fun and interesting.",
        "Natural language processing is challenging but rewarding.",
        "Deep learning models require lots of data.",
        "Python is a great language for data science.",
        "Neural networks can solve complex problems.",
        "Data preprocessing is an important step in ML."
    ]
    
    # Target labels (for demonstration)
    labels = [0, 0, 1, 0, 1, 0]  # Binary classification for demo
    
    # Vectorize text using various techniques
    
    # Count Vectorizer (Bag of Words)
    count_vec = CountVectorizer()
    X_count = count_vec.fit_transform(documents)
    
    # TF-IDF Vectorizer
    tfidf_vec = TfidfVectorizer()
    X_tfidf = tfidf_vec.fit_transform(documents)
    
    # Print shapes
    print(f"Count Vectorizer: {X_count.shape}")
    print(f"TF-IDF Vectorizer: {X_tfidf.shape}")
    
    # Simple classification with TF-IDF features
    X_train, X_test, y_train, y_test = train_test_split(X_tfidf, labels, test_size=0.33, random_state=42)
    
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    
    # Logistic Regression
    lr = LogisticRegression(max_iter=200)
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    
    # Naive Bayes
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    nb_pred = nb.predict(X_test)
    
    print("NLP classification with different classifiers:")
    print(f"Logistic Regression accuracy: {accuracy_score(y_test, lr_pred):.4f}")
    print(f"Naive Bayes accuracy: {accuracy_score(y_test, nb_pred):.4f}")

# ====== Neural Network Examples ======

def test_pytorch_basics():
    """Test basic PyTorch neural network"""
    if not TORCH_AVAILABLE:
        print("Skipping test_pytorch_basics: PyTorch not available")
        return
    
    print("Running PyTorch basics test...")
    
    # Set random seed for reproducibility
    torch.manual_seed(42)
    
    # Generate synthetic classification data
    X_numpy = np.random.randn(100, 10)  # 100 samples, 10 features
    y_numpy = np.random.randint(0, 2, size=100)  # Binary labels
    
    # Convert to PyTorch tensors
    X = torch.FloatTensor(X_numpy)
    y = torch.LongTensor(y_numpy)
    
    # Define simple neural network
    class SimpleNN(nn.Module):
        def __init__(self, input_size, hidden_size, output_size):
            super(SimpleNN, self).__init__()
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(hidden_size, output_size)
        
        def forward(self, x):
            out = self.fc1(x)
            out = self.relu(out)
            out = self.fc2(out)
            return out
    
    input_size = 10
    hidden_size = 20
    output_size = 2  # Binary classification
    
    # Initialize model
    model = SimpleNN(input_size, hidden_size, output_size)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    # Training loop
    num_epochs = 100
    for epoch in range(num_epochs):
        # Forward pass
        outputs = model(X)
        loss = criterion(outputs, y)
        
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 20 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")
    
    # Test model
    model.eval()
    with torch.no_grad():
        outputs = model(X)
        _, predicted = torch.max(outputs.data, 1)
        accuracy = (predicted == y).sum().item() / y.size(0)
    
    print(f"PyTorch model training completed. Accuracy: {accuracy:.4f}")

def test_tensorflow_basics():
    """Test basic TensorFlow/Keras neural network"""
    if not TF_AVAILABLE:
        print("Skipping test_tensorflow_basics: TensorFlow not available")
        return
    
    print("Running TensorFlow/Keras basics test...")
    
    # Set random seed for reproducibility
    tf.random.set_seed(42)
    np.random.seed(42)
    
    # Generate synthetic classification data
    X_train = np.random.randn(100, 10)  # 100 samples, 10 features
    y_train = np.random.randint(0, 2, size=100)  # Binary labels
    
    # Define model architecture
    model = keras.Sequential([
        layers.Dense(20, activation='relu', input_shape=(10,)),
        layers.Dense(10, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Train model
    history = model.fit(
        X_train, y_train,
        epochs=50,
        verbose=0,
        validation_split=0.2
    )
    
    # Evaluate model
    loss, accuracy = model.evaluate(X_train, y_train, verbose=0)
    print(f"TensorFlow/Keras model training completed. Accuracy: {accuracy:.4f}")

# ====== Advanced ML Examples ======

def test_hyperparameter_tuning():
    """Test hyperparameter tuning with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_hyperparameter_tuning: scikit-learn not available")
        return
    
    print("Running hyperparameter tuning test...")
    
    # Load dataset
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Define model and parameter grid
    from sklearn.svm import SVC
    
    model = SVC()
    param_grid = {
        'C': [0.1, 1, 10, 100],
        'gamma': [0.001, 0.01, 0.1, 1],
        'kernel': ['rbf', 'linear']
    }
    
    # Perform grid search
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring='accuracy',
        verbose=0
    )
    
    grid_search.fit(X_train, y_train)
    
    # Get best parameters and score
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    
    print(f"Best parameters: {best_params}")
    print(f"Best cross-validation score: {best_score:.4f}")
    
    # Evaluate on test set
    best_model = grid_search.best_estimator_
    test_score = best_model.score(X_test, y_test)
    
    print(f"Test accuracy with best model: {test_score:.4f}")

def test_ensemble_methods():
    """Test ensemble methods with sklearn"""
    if not SKLEARN_AVAILABLE:
        print("Skipping test_ensemble_methods: scikit-learn not available")
        return
    
    print("Running ensemble methods test...")
    
    # Load dataset
    breast_cancer = load_breast_cancer()
    X, y = breast_cancer.data, breast_cancer.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Define ensemble models
    from sklearn.ensemble import (
        RandomForestClassifier,
        GradientBoostingClassifier,
        AdaBoostClassifier,
        VotingClassifier
    )
    from sklearn.linear_model import LogisticRegression
    
    # Individual models
    rf = RandomForestClassifier(random_state=42)
    gb = GradientBoostingClassifier(random_state=42)
    ada = AdaBoostClassifier(random_state=42)
    
    # Voting ensemble
    voting_clf = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('ada', ada)],
        voting='soft'
    )
    
    # Train and evaluate individual models
    models = {
        "Random Forest": rf,
        "Gradient Boosting": gb,
        "AdaBoost": ada,
        "Voting Ensemble": voting_clf
    }
    
    results = {}
    
    for name, model in models.items():
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        results[name] = {
            "accuracy": accuracy,
            "f1_score": f1
        }
        
        print(f"{name}: Accuracy = {accuracy:.4f}, F1 Score = {f1:.4f}")

# ====== Main execution ======

def run_all_ml_tests():
    """Run all machine learning tests"""
    
    # Basic ML tests
    print("\n===== Testing Basic Classification =====")
    test_basic_classification()
    
    print("\n===== Testing Regression =====")
    test_regression()
    
    print("\n===== Testing Clustering =====")
    test_clustering()
    
    # NLP tests
    print("\n===== Testing NLP Basics =====")
    test_nlp_basics()
    
    # Neural Networks
    print("\n===== Testing PyTorch Basics =====")
    test_pytorch_basics()
    
    print("\n===== Testing TensorFlow Basics =====")
    test_tensorflow_basics()
    
    # Advanced ML techniques
    print("\n===== Testing Hyperparameter Tuning =====")
    test_hyperparameter_tuning()
    
    print("\n===== Testing Ensemble Methods =====")
    test_ensemble_methods()

if __name__ == "__main__":
    print("Running Advanced Machine Learning Tests")
    print(f"scikit-learn available: {SKLEARN_AVAILABLE}")
    print(f"PyTorch available: {TORCH_AVAILABLE}")
    print(f"TensorFlow available: {TF_AVAILABLE}")
    run_all_ml_tests()
    print("All ML tests completed") 