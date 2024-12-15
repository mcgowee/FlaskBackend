from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

def train_model():
    iris = load_iris()
    X, y = iris.data, iris.target
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)
    return model

model = train_model()
