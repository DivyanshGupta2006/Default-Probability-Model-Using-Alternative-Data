import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. Load and Prepare Data ---
# In a real project, you would load this from a CSV file.
# Here, we'll create a sample DataFrame for demonstration.
data = {
    'age': [25, 30, 35, 40, 45, 22, 55, 60, 65, 70],
    'income': [50000, 60000, 80000, 100000, 120000, 40000, 150000, 180000, 200000, 220000],
    'existing_loans': [1, 2, 1, 0, 1, 0, 2, 3, 1, 2],
    'default': [0, 0, 0, 0, 0, 1, 0, 1, 0, 1]  # 1 = Default, 0 = No Default
}
df = pd.DataFrame(data)

# Separate features (X) from the target variable (y)
X = df[['age', 'income', 'existing_loans']]
y = df['default']

# --- 2. Split Data into Training and Testing Sets ---
# This is crucial to evaluate how the model performs on new, unseen data.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# --- 3. Initialize and Train the Model ---
# We create an instance of the LogisticRegression model.
model = LogisticRegression(random_state=42)

# We train the model using our training data.
print("Training the model...")
model.fit(X_train, y_train)
print("Model training complete.")

# --- 4. Make Predictions ---
# The model predicts labels (0 or 1) on the test set.
y_pred = model.predict(X_test)

# --- 5. Evaluate the Model ---
print("\n--- Model Evaluation ---")

# Accuracy: How many predictions were correct?
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2%}")

# Classification Report: Provides precision, recall, and f1-score.
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix: Shows correct vs. incorrect predictions for each class.
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Optional: Visualize the Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()


# --- 6. Interpret the Coefficients (Transparency) ---
print("\n--- Model Coefficients ---")
# The coefficients show the influence of each feature on the prediction.
coefficients = pd.DataFrame(model.coef_[0], X.columns, columns=['Coefficient'])
print(coefficients)