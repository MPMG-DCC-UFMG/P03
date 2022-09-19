import glob
import sys
import torch

import pandas as pd

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

classes = {
  0: 'Produtos',
  1: 'Serviços Públicos e Privados',
  2: 'Serviços regulamentados pela ANATEL',
  3: 'Finanças',
  4: 'Publicidade',
  5: 'Outros'
  }

predicts = []

working_dir = sys.argv[1]

for filename in glob.iglob(f'{working_dir}/*.prd'):
  x = torch.load(filename)
  for i in range(10):
    predicts.append(classes[x[i]['pred_cls']])

plot_dist(predicts, "reclameaqui_bert")
