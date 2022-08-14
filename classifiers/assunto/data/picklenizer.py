import re
import json
import os
import pickle
import sys

import pandas as pd
import numpy as np

from pyhive import hive
from sklearn.model_selection import KFold

working_dir = sys.argv[1]

# Getting Data
con = hive.Connection(host="", port="", username="", auth="LDAP", password="")

df = pd.read_sql("SELECT manifestacao.mensagem_show AS text, sub_classe.nom_sub_classe AS lbl FROM ouvidoria.manifestacao AS manifestacao LEFT JOIN ouvidoria.assunto AS assunto ON assunto.id_manifestacao = manifestacao.id_manifestacao LEFT JOIN stage.ouvidoria_20211217_sub_classe AS sub_classe ON sub_classe.id_sub_classe = assunto.id_sub_classe WHERE manifestacao.id_ouvidoria = 14", con)

df = df.replace({np.nan: None, 'NONE': None, '': None})
df = df.astype(object).where(df.notna(), None)
df = df.dropna(subset=['text'])
df.drop(df[df.text.str.len() < 50].index, inplace=True)

df['idx'] = df.index

# Trimming Classes (Top 5 most frenquent + others)

df['cls'] = " "

classes = {
  'Produtos':0,
  'Serviços Públicos e Privados':1,
  'Serviços regulamentados pela ANATEL':2,
  'Finanças':3,
  'Publicidade':4
  }

for i in df.index:
  if df.at[i, 'lbl'] not in classes:
    df.at[i, 'cls'] = 5
  else:
    df.at[i, 'cls'] = classes[df.at[i, 'lbl']]

os.makedirs(working_dir, exist_ok=True)

js = df.to_json(orient='records')
parsed = json.loads(js)

with open(working_dir + 'samples.pkl', 'wb') as f:
  pickle.dump(parsed, f)

fold = 0

kf = KFold(n_splits=10)

for train_index, test_index in kf.split(df):
  val_index = train_index[:len(test_index)].tolist()
  train_index = train_index[len(test_index):].tolist()
  test_index = test_index.tolist()

  path = working_dir + 'fold_' + str(fold)
  
  os.makedirs(path, exist_ok=True)
  
  with open(path + '/train.pkl', 'wb') as f:
    pickle.dump(train_index, f)
    
  with open(path + '/test.pkl', 'wb') as f:
    pickle.dump(test_index, f)

  with open(path + '/val.pkl', 'wb') as f:
    pickle.dump(val_index, f)

  fold += 1
