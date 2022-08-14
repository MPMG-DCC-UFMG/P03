import sys
import json 

import pandas as pd

from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from spacy.lang.pt.stop_words import STOP_WORDS as pt_stop

# reading data
working_dir = sys.argv[1]

ds = pd.read_pickle(working_dir + 'samples.pkl')

df = pd.DataFrame(ds)

# tf-idfying  
vectorizer = TfidfVectorizer(lowercase=True, stop_words=list(pt_stop))

vectorizer.fit(df['text'])

X_tfidf_vectorize = vectorizer.transform(df['text'])
y = df['cls'].to_numpy()

# setting up model
SVM = svm.SVC(C='1.0', kernel='linear', degree=3, gamma='auto')

stats = pd.DataFrame(columns=["fold"])

for fold in range(10):
  SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')

  train_index = pd.read_pickle(working_dir + 'fold_' + str(fold) + '/train.pkl')
  val_index = pd.read_pickle(working_dir + 'fold_' + str(fold) + '/val.pkl')
  test_index = pd.read_pickle(working_dir + 'fold_' + str(fold) + '/test.pkl')

  X_train, y_train = X_tfidf_vectorize[train_index], y[train_index]
  X_val, y_val = X_tfidf_vectorize[val_index], y[val_index]
  X_test, y_test = X_tfidf_vectorize[test_index], y[test_index]

  SVM.fit(X_train, y_train)

  y_pred = SVM.predict(X_test)
  
  stats.at[fold, "Mic-F1"] = f1_score(y_test, y_pred, average='micro')
  stats.at[fold, "Mac-F1"] = f1_score(y_test, y_pred, average='macro')
  stats.at[fold, "Wei-F1"] = f1_score(y_test, y_pred, average='weighted')
  
  print("fold " + str(fold) + " done")

stats.to_csv("SVM" + ".stat", sep='\t', index=False, header=True)
