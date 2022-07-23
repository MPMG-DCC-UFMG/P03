import psycopg2
import psycopg2.extras
import time
import sys

import pandas as pd
import numpy as np

from config import config

# Connect to PostgreSQL
params = config(config_db = 'credentials.ini')
con = psycopg2.connect(**params)
cur = con.cursor()
print('Python connected to PostgreSQL!')

page_size = 100000

# Loading data
df = pd.read_csv(sys.argv[1], compression='gzip')
df = df.dropna(subset=['conteudo'])

df['nome_completo_empresa'] = df['nome_completo_empresa'].str.lower().str.strip()
df['cidade'] = df['cidade'].str.lower().str.strip()
df['estado'] = df['estado'].str.lower().str.strip()

tic = time.perf_counter()

# FIRST PASS
# Getting entidades

entidades_values = []
entidades_query = """
  INSERT INTO entidade
    (nome, sinonimos, fuzzy_matching)
  VALUES
    (%s, '', FALSE)
  ON CONFLICT
    (nome)
  DO NOTHING;
  """
  
empresas_temp = set(df['nome_completo_empresa'].dropna())
location_temp = df[['cidade','estado']].dropna(how='any')

entidades_values += [tuple([x]) for x in empresas_temp]
entidades_values += [tuple([x]) for x in set(location_temp['cidade'])]
entidades_values += [tuple([x]) for x in set(location_temp['estado'])]

psycopg2.extras.execute_batch(cur, entidades_query, entidades_values, page_size=page_size)

cur.execute("""
  SELECT nome, id
  FROM entidade;
  """)
  
entidades = dict(cur.fetchall())

toc = time.perf_counter(); print(f"FIRST PASS done! {toc - tic:0.4f}"); tic = time.perf_counter()
# SECOND PASS
# Getting empresas and localidades

empresas_values = [tuple([entidades[x]]) for x in empresas_temp]

empresas_query = """
	INSERT INTO empresa
    (entidade_id)
  VALUES
    (%s)
  ON CONFLICT
    (entidade_id)
  DO NOTHING;
  """

psycopg2.extras.execute_batch(cur, empresas_query, empresas_values, page_size=page_size)

localidades_values = [tuple([entidades[cidade], entidades[uf]]) for cidade, uf in zip(location_temp['cidade'], location_temp['estado'])]

localidades_query = """
  INSERT INTO localidade
    (cidade_entidade_id, uf_entidade_id)
  VALUES
    (%s, %s)
  ON CONFLICT
    (cidade_entidade_id, uf_entidade_id)
  DO NOTHING;
  """
  
psycopg2.extras.execute_batch(cur, localidades_query, localidades_values, page_size=page_size)

cur.execute("""
  SELECT entidade.nome, empresa.id
  FROM entidade
  INNER JOIN empresa
    ON entidade.id = empresa.entidade_id
  WHERE entidade.nome IN ('""" + "', '".join(empresas_temp) + """');
  """)

empresas = dict(cur.fetchall())
empresas[None] = None

cur.execute("""
  SELECT CONCAT(cidade.nome, uf.nome), localidade.id 
  FROM localidade 
  INNER JOIN entidade AS cidade 
    ON localidade.cidade_entidade_id = cidade.id 
  INNER JOIN entidade AS uf 
    ON localidade.uf_entidade_id = uf.id;
  """)

localidades = dict(cur.fetchall())
localidades[None] = None

toc = time.perf_counter(); print(f"SECOND PASS done! {toc - tic:0.4f}"); tic = time.perf_counter()
# THIRD PASS
# Getting reclamacoes

reclamacoes_values = []
reclamacoes_query = """
  INSERT INTO reclamacao
    (plataforma, data, id_empresa, id_localidade, id_interno) 
  VALUES
    ('reclameaqui', TO_DATE(%s,'YYYY-MM-DD'), %s, %s, %s)
  ON CONFLICT
    (id_interno)
  DO NOTHING;
  """

df['Localidade'] = np.where(df['cidade'] is None or df['estado'] is None, None, df['cidade'] + df['estado'])
df['Localidade'] = df.Localidade.replace(localidades).replace({np.nan: None})

df['nome_completo_empresa'] = df.nome_completo_empresa.replace(empresas)

reclamacoes_values = [tuple(x) for x in df[['data_criacao', 'nome_completo_empresa', 'Localidade', 'id']].to_numpy()]

psycopg2.extras.execute_batch(cur, reclamacoes_query, reclamacoes_values, page_size=page_size)

cur.execute("""
  SELECT id_interno, id 
  FROM reclamacao 
  WHERE reclamacao.plataforma = 'reclameaqui';
  """)
  
reclamacoes = dict(cur.fetchall())

toc = time.perf_counter(); print(f"THIRD PASS done! {toc - tic:0.4f}"); tic = time.perf_counter()
# FOURTH PASS

reclamacoes_plataforma_values = []
reclamacoes_plataforma_query = """
  INSERT INTO reclamacao_reclameaqui
    (id_reclamacao, titulo, categorias)
  VALUES
    (%s, %s, %s)
  ON CONFLICT
    (id_reclamacao)
  DO NOTHING;
  """

historico_values = []
historico_query = """
  INSERT INTO historico
    (autor, texto, data, id_reclamacao, ordem) 
  VALUES 
    (%s, %s, TO_DATE(%s,'YYYY-MM-DD'), %s, %s)
  ON CONFLICT
    (id_reclamacao, ordem)
  DO NOTHING;
  """
  
df['Reclamacao'] = df.id.replace(reclamacoes)

reclamacoes_plataforma_values = [tuple(x) for x in df[['Reclamacao', 'Titulo', 'Categorias']].to_numpy()]
historico_values = [tuple(['consumidor'] + list(x) + [1]) for x in df[['conteudo', 'data_criacao', 'Reclamacao']].to_numpy()]
historico_values += [tuple(['nome_completo_empresa'] + list(x) + [2]) for x in df[['Resposta', 'data_criacao', 'Reclamacao']].dropna(subset=['Resposta']).to_numpy()]

psycopg2.extras.execute_batch(cur, reclamacoes_plataforma_query, reclamacoes_plataforma_values, page_size=page_size)
psycopg2.extras.execute_batch(cur, historico_query, historico_values, page_size=page_size)

toc = time.perf_counter(); print(f"FOURTH PASS done! {toc - tic:0.4f}")

#con.commit()
#con.close()

print("committed")
