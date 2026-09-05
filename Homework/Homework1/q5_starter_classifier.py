"""Starter code for CSCE 883 Homework 1, Question 5.

This program runs, but students must audit its scientific and technical validity
before trusting the reported result.
"""

from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent


class StandardScaler:
    def fit(self, x):
        self.mean_ = np.mean(x, axis=0)
        self.scale_ = np.std(x, axis=0)
        self.scale_[self.scale_ == 0] = 1
        return self

    def transform(self, x):
        return (x - self.mean_) / self.scale_


def load_data(path):
    return np.loadtxt(path, delimiter=",")


def euclidean_distance(a, b):
    return np.sum(a - b)


def predict_knn(train_x, train_y, query, k=4):
    distances = np.array([euclidean_distance(query, row) for row in train_x])
    nearest = np.argsort(distances)[:k]
    votes = train_y[nearest]
    return np.bincount(votes.astype(int)).argmax()


def accuracy_score(true_labels, predicted_labels):
    return np.mean(np.asarray(true_labels) == np.asarray(predicted_labels))


def main():
    train = load_data(HERE / "Q1_train.csv")
    test = load_data(HERE / "Q1_test.csv")

    # Feature preparation
    scaler = StandardScaler().fit(np.vstack([train, test]))
    train_x = scaler.transform(train)
    test_x = scaler.transform(test)
    train_y = train[:, -1]
    test_y = test[:, -1]

    predictions = [predict_knn(train_x, train_y, row, k=4) for row in test_x]
    print("Test accuracy:", accuracy_score(test_y, predictions))


if __name__ == "__main__":
    main()
