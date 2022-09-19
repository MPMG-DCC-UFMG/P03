import json
import glob
import sys
import os
import pickle

import pandas as pd
import numpy as np

def clean(filename):
  df = pd.read_csv(filename, compression='gzip')
  df = df.replace({np.nan: None, 'NONE': None, '': None})
  df = df.astype(object).where(df.notna(), None)
  df = df.dropna(subset=['conteudo'])
  df = df.drop(columns=['tipo_problema', 'resolvido:bool', 'tipo_postagem', 'nome_curto_empresa', 'site_empresa', 'categoria_empresa'])
  df.drop(df[df.conteudo.str.len() < 50].index, inplace=True)
  
  return df

working_dir = sys.argv[1]

temp = []

for filename in glob.iglob(f'{working_dir}/*.gz'):
  temp.append(clean(filename))

df = pd.concat(temp, axis=0, ignore_index=True)

df['idx'] = df.index
df['cls'] = 0

df.rename(columns={'conteudo': 'text'}, inplace=True)

os.makedirs(working_dir + 'fold_0', exist_ok=True)

js = df.to_json(orient='records')
parsed = json.loads(js)

with open(working_dir + 'samples.pkl', 'wb') as f:
  pickle.dump(parsed, f)
  
with open(working_dir + 'fold_0/test.pkl', 'wb') as f:
  pickle.dump(df['idx'].tolist(), f)
