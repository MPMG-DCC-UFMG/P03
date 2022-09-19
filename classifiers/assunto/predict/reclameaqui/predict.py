import sys
import json 
import joblib

import pandas as pd

from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from spacy.lang.pt.stop_words import STOP_WORDS as pt_stop
from collections import Counter
from matplotlib import pyplot as plt

def plot_dist(labels, file_name):
  # summarize distribution
  counter = Counter(labels)
  
  counter = dict(sorted(counter.items(), key=lambda x: (x[1], x[0])))

  for k,v in counter.items():
	  per = v / len(labels) * 100
	  
	  print('Class=%s, n=%d (%.3f%%)' % (k, v, per))

  # plot the distribution
  plt.figure(figsize=(10, len(counter)/3))
  plt.barh(list(counter.keys()), list(counter.values()))
  plt.tight_layout()
  plt.savefig(file_name + ".png")

# reading data
working_dir = sys.argv[1]

predicts = []

ds = pd.read_pickle(working_dir + 'samples.pkl')

df = pd.DataFrame(ds)

with open('/home/felipe/Dropbox/Github/P03/classifiers/assunto/models/svm/output/TfidfVectorizer.sav', 'rb') as f1:
  vectorizer = joblib.load(f1)
  
X_tfidf_vectorize = vectorizer.transform(df['text'])

for fold in range(10):
  print("fold " + str(fold))
  with open('/home/felipe/Dropbox/Github/P03/classifiers/assunto/models/svm/output/' + 'svm_fold_' + str(fold) + '.sav', 'rb') as f2:
    SVM = joblib.load(f2)
  
  predicts = SVM.predict(X_tfidf_vectorize)

print(predicts)

df = pd.DataFrame (predicts, columns = ['pred'])

classes = {
  0: 'Produtos',
  1: 'Serviços Públicos e Privados',
  2: 'Serviços regulamentados pela ANATEL',
  3: 'Finanças',
  4: 'Publicidade',
  5: 'Outros'
  }
  
print(df['pred'])
  
plot_dist(df['pred'].map(classes), "reclameaqui_svm")
