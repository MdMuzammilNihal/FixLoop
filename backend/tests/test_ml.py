# Machine Learning test with scikit-learn

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Generate synthetic classification dataset
def generate_data(n_samples=1000, n_features=2, n_classes=2, random_state=42):
    try:
        from sklearn.datasets import make_classification
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_features,
            n_redundant=0,
            n_classes=n_classes,
            random_state=random_state
        )
        return X, y
    except ImportError:
        # Fallback if sklearn is not available
        np.random.seed(random_state)
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, n_classes, size=n_samples)
        return X, y

# Train multiple models and evaluate their performance
def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    # Dictionary to store models
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'SVM': SVC(random_state=42, probability=True)
    }
    
    # Dictionary to store results
    results = {}
    
    # Train and evaluate each model
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        
        # Store results
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        print(f"{name} Accuracy: {accuracy:.4f}")
    
    return results

# Visualize model comparison
def plot_model_comparison(results):
    model_names = list(results.keys())
    accuracies = [results[name]['accuracy'] for name in model_names]
    
    plt.figure(figsize=(10, 6))
    plt.bar(model_names, accuracies, color='skyblue')
    plt.title('Model Accuracy Comparison')
    plt.xlabel('Model')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1.0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add accuracy values on top of the bars
    for i, acc in enumerate(accuracies):
        plt.text(i, acc + 0.01, f'{acc:.4f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('model_comparison.png')
    plt.close()
    return 'model_comparison.png'

# Visualize the confusion matrix
def plot_confusion_matrix(y_test, y_pred, class_names=None):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    
    if class_names is None:
        class_names = [f'Class {i}' for i in range(cm.shape[0])]
    
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)
    
    # Add text annotations
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                     ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black")
    
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig('confusion_matrix.png')
    plt.close()
    return 'confusion_matrix.png'

# Main execution
if __name__ == "__main__":
    try:
        # Generate synthetic data
        X, y = generate_data(n_samples=500, n_features=10, n_classes=2)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Scale the features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        # Train and evaluate models
        results = train_and_evaluate_models(X_train, X_test, y_train, y_test)
        
        # Determine the best model
        best_model_name = max(results, key=lambda x: results[x]['accuracy'])
        best_model = results[best_model_name]['model']
        
        print(f"\nBest model: {best_model_name} with accuracy: {results[best_model_name]['accuracy']:.4f}")
        
        # Make predictions with the best model
        y_pred = best_model.predict(X_test)
        
        # Plot model comparison
        comparison_plot = plot_model_comparison(results)
        
        # Plot confusion matrix
        conf_matrix_plot = plot_confusion_matrix(y_test, y_pred)
        
        print(f"\nGenerated plots: {comparison_plot}, {conf_matrix_plot}")
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
    except ImportError as e:
        print(f"Error importing required library: {e}")
        print("Please make sure scikit-learn is installed.")
    except Exception as e:
        print(f"An error occurred: {e}") 