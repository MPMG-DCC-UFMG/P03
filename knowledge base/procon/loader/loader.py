import psycopg2
import psycopg2.extras
import time
import re

import pandas as pd
import numpy as np

from config import config
from pyhive import hive

con = hive.Connection(host="localhost", port="10500", username="ufmg.fcosta", auth='LDAP', password="Felipe3432***")

df = pd.read_sql("SELECT manifestacao.metadata_arquivo_linha, manifestacao.data_alerta_show, manifestacao.data_manifestacao_show, manifestacao.flg_sigilo, manifestacao.id_documento_sgdp, manifestacao.nota_avaliacao, manifestacao.num_manifestacao, manifestacao.avaliacao_show, manifestacao.senha, manifestacao.mensagem_show, manifestacao.num_versao, manifestacao.data_ultima_alteracao_show, manifestacao.usuario_ultima_alteracao_show, manifestacao.id_manifestacao, manifestacao.id_forma_resposta, manifestacao.id_forma_contato, manifestacao.id_objetivo, manifestacao.id_prioridade, manifestacao.id_situacao, manifestacao.id_promotoria_pgjmp, manifestacao.id_comarca_pgjmp, manifestacao.id_ouvidoria, manifestacao.id_sub_classe, manifestacao.id_pessoa, manifestacao.data_conclusao_show, manifestacao.usuario_inclusao_show, manifestacao.id_aplicacao_inclusao, manifestacao.id_aplicacao_ult_alteracao, manifestacao.nome_outros_orgaos_show, manifestacao.nome_justificativa_sigilo_show, manifestacao.nome_login_usuario_finalizacao_show, manifestacao.nome_login_distribuicao_secretaria_show, manifestacao.data_distribuicao_secretaria_show, manifestacao.id_finalizacao, manifestacao.sgl_unidade_federativa_show, manifestacao.cod_grau_instrucao, manifestacao.id_sexo, manifestacao.flg_anonimo, manifestacao.nome_logradouro_show, manifestacao.nome_complemento_show, manifestacao.nome_bairro_show, manifestacao.nome_municipio_show, manifestacao.cep, manifestacao.num_logradouro, manifestacao.ddd_celular, manifestacao.telefone_celular, manifestacao.ddd_fixo, manifestacao.telefone_fixo, manifestacao.cpf, manifestacao.cnpj, manifestacao.rg, manifestacao.nome_pessoa_show, manifestacao.data_nascimento_show, manifestacao.nome_mae_show, manifestacao.nome_email_show, manifestacao.id_tipo_pessoa, manifestacao.flg_conferido, manifestacao.flg_enviado, manifestacao.data_enc_orgao_externo_show, manifestacao.id_tipo_pessoa_fornecedor, manifestacao.nome_pessoa_fornecedor_show, manifestacao.cpf_fornecedor, manifestacao.cnpj_fornecedor, manifestacao.cep_fornecedor, manifestacao.nome_logradouro_fornecedor_show, manifestacao.num_logradouro_fornecedor, manifestacao.nome_complemento_fornecedor_show, manifestacao.nome_municipio_fornecedor_show, manifestacao.nome_bairro_fornecedor_show, manifestacao.sgl_uf_fornecedor, manifestacao.nome_site_fornecedor_show, manifestacao.nome_email_fornecedor_show, manifestacao.ddd_fixo_fornecedor, manifestacao.telefone_fixo_fornecedor, manifestacao.ip_address, manifestacao.ip_country, manifestacao.ip_region, manifestacao.ip_city, manifestacao.ip_isp, manifestacao.ip_organization, manifestacao.ip_domain_name, manifestacao.nome_cidade_ocorrencia_show, manifestacao.nome_envolvidos_show, manifestacao.data_hora_fatos_show, manifestacao.nome_testemunhas_show, manifestacao.manifestacao_outro_orgao, manifestacao.metadata_arquivo, manifestacao.metadata_data_ingestao, manifestacao.metadata_data_referencia, sub_classe.nom_sub_classe, infracao.nom_infracao, area.nom_area, classe.nom_classe FROM ouvidoria.manifestacao AS manifestacao LEFT JOIN ouvidoria.infracao_manifestacao AS infracao_manifestacao ON infracao_manifestacao.id_manifestacao = manifestacao.id_manifestacao LEFT JOIN stage.ouvidoria_20211217_infracao AS infracao ON infracao.id_infracao = infracao_manifestacao.id_infracao LEFT JOIN ouvidoria.area_manifestacao AS area_manifestacao ON manifestacao.id_manifestacao = area_manifestacao.id_manifestacao LEFT JOIN stage.ouvidoria_20211217_area AS area ON area.id_area = area_manifestacao.id_area LEFT JOIN ouvidoria.area_grupo AS area_grupo ON area_grupo.id_area_grupo = area.id_area_grupo LEFT JOIN ouvidoria.assunto AS assunto ON assunto.id_manifestacao = manifestacao.id_manifestacao LEFT JOIN stage.ouvidoria_20211217_sub_classe AS sub_classe ON sub_classe.id_sub_classe = assunto.id_sub_classe LEFT JOIN stage.ouvidoria_20211217_classe AS classe ON classe.id_classe = sub_classe.id_classe LEFT JOIN stage.ouvidoria_20211217_finalizacao AS finalizacao ON CAST (finalizacao.id_finalizacao AS INTEGER) = manifestacao.id_finalizacao LEFT JOIN ouvidoria.forma_contato as forma_contato ON manifestacao.id_forma_contato = forma_contato.id_forma_contato LEFT JOIN ouvidoria.objetivo as objetivo ON manifestacao.id_objetivo = objetivo.id_objetivo LEFT JOIN ouvidoria.situacao as situacao ON manifestacao.id_situacao = situacao.id_situacao LEFT JOIN ouvidoria.grau_instrucao as grau_instrucao ON manifestacao.cod_grau_instrucao = grau_instrucao.cod_grau_instrucao WHERE manifestacao.id_ouvidoria = 14", con)

df = df.replace({np.nan: None, 'NONE': None, '': None})
df = df.astype(object).where(df.notna(), None)

def maybe_rename(col_name):
  return re.sub(r'.*\.', '', col_name)

df = df.rename(columns=maybe_rename)

df = df.dropna(subset=['mensagem_show'])

df['nome_pessoa_fornecedor_show'] = df['nome_pessoa_fornecedor_show'].str.lower().str.strip()
df['nome_municipio_show'] = df['nome_municipio_show'].str.lower().str.strip()
df['sgl_unidade_federativa_show'] = df['sgl_unidade_federativa_show'].str.lower().str.strip()

df['metadata_arquivo_linha'] = df['metadata_arquivo_linha'].astype('int')

# Connect to PostgreSQL
params = config(config_db = 'credentials.ini')
con = psycopg2.connect(**params)
cur = con.cursor()
print('Python connected to PostgreSQL!')

page_size = 10000

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

empresas_temp = set(df['nome_pessoa_fornecedor_show'].dropna())
location_temp = df[['nome_municipio_show','sgl_unidade_federativa_show']].dropna(how='any')

entidades_values += [tuple([x]) for x in empresas_temp]
entidades_values += [tuple([x]) for x in set(location_temp['nome_municipio_show'])]
entidades_values += [tuple([x]) for x in set(location_temp['sgl_unidade_federativa_show'])]

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

localidades_values = [tuple([entidades[cidade], entidades[uf]]) for cidade, uf in zip(location_temp['nome_municipio_show'], location_temp['sgl_unidade_federativa_show'])]

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

cur.execute("""
  SELECT CONCAT(cidade.nome, uf.nome), localidade.id 
  FROM localidade 
  INNER JOIN entidade AS cidade 
    ON localidade.cidade_entidade_id = cidade.id 
  INNER JOIN entidade AS uf 
    ON localidade.uf_entidade_id = uf.id;
  """)

localidades = dict(cur.fetchall())

df['Localidade'] = np.where(df['nome_municipio_show'] is None or df['sgl_unidade_federativa_show'] is None, None, df['nome_municipio_show'] + df['sgl_unidade_federativa_show'])
df['Localidade'] = df['Localidade'].map(localidades)

df['Empresa'] = df['nome_pessoa_fornecedor_show'].map(empresas)

df = df.astype(object).where(df.notna(), None)

toc = time.perf_counter(); print(f"SECOND PASS done! {toc - tic:0.4f}"); tic = time.perf_counter()

# THIRD PASS
# Getting reclamacoes

reclamacoes_values = []
reclamacoes_query = """
  INSERT INTO reclamacao
    (plataforma, data, id_empresa, id_localidade, id_interno) 
  VALUES
    ('procon', TO_DATE(%s,'YYYY-MM-DD'), %s, %s, %s)
  ON CONFLICT
    (id_interno)
  DO NOTHING;
  """

reclamacoes_values = [tuple(x) for x in df[['data_manifestacao_show', 'Empresa', 'Localidade', 'metadata_arquivo_linha']].to_numpy()]

psycopg2.extras.execute_batch(cur, reclamacoes_query, reclamacoes_values, page_size=page_size)

cur.execute("""
  SELECT id_interno, id 
  FROM reclamacao 
  WHERE reclamacao.plataforma = 'procon';
  """)
  
reclamacoes = dict(cur.fetchall())

toc = time.perf_counter(); print(f"THIRD PASS done! {toc - tic:0.4f}"); tic = time.perf_counter()

# FOURTH PASS
columns = ['num_manifestacao', 'data_alerta_show', 'flg_sigilo', 'id_documento_sgdp', 'nota_avaliacao', 'avaliacao_show', 'senha', 'num_versao', 'data_ultima_alteracao_show', 'usuario_ultima_alteracao_show', 'id_manifestacao', 'id_objetivo', 'id_prioridade', 'id_comarca_pgjmp', 'id_ouvidoria', 'id_pessoa', 'data_conclusao_show', 'usuario_inclusao_show', 'nome_outros_orgaos_show', 'nome_justificativa_sigilo_show', 'nome_login_usuario_finalizacao_show', 'nome_login_distribuicao_secretaria_show', 'data_distribuicao_secretaria_show', 'flg_anonimo', 'flg_conferido', 'flg_enviado', 'data_enc_orgao_externo_show', 'id_tipo_pessoa_fornecedor', 'cpf_fornecedor', 'cnpj_fornecedor', 'cep_fornecedor', 'nome_logradouro_fornecedor_show', 'num_logradouro_fornecedor', 'nome_complemento_fornecedor_show', 'nome_municipio_fornecedor_show', 'nome_bairro_fornecedor_show', 'sgl_uf_fornecedor', 'nome_site_fornecedor_show', 'nome_email_fornecedor_show', 'ddd_fixo_fornecedor', 'telefone_fixo_fornecedor', 'ip_address', 'ip_country', 'ip_region', 'ip_city', 'ip_isp', 'ip_organization', 'ip_domain_name', 'nome_envolvidos_show', 'data_hora_fatos_show', 'nome_testemunhas_show', 'manifestacao_outro_orgao', 'metadata_arquivo', 'metadata_data_ingestao', 'metadata_data_referencia', 'nom_area', 'nom_sub_classe', 'nom_classe', 'id_forma_resposta', 'id_forma_contato', 'id_situacao', 'id_sub_classe', 'id_finalizacao', 'nome_logradouro_show', 'nome_complemento_show', 'nome_bairro_show', 'cep', 'num_logradouro', 'ddd_celular', 'telefone_celular', 'ddd_fixo', 'telefone_fixo', 'cpf', 'cnpj', 'rg', 'nome_pessoa_show', 'data_nascimento_show', 'nome_mae_show', 'nome_email_show', 'id_tipo_pessoa', 'nome_cidade_ocorrencia_show']

reclamacoes_plataforma_values = []
reclamacoes_plataforma_query = """
  INSERT INTO reclamacao_procon
    (id_reclamacao, """ + ", ".join(columns) + """)
  VALUES
    (%s """ + ", %s" * len(columns) + """)
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

df['Reclamacao'] = df['metadata_arquivo_linha'].astype(str).map(reclamacoes)

reclamacoes_plataforma_values = [tuple(x) for x in df[['Reclamacao'] + columns].to_numpy()]
historico_values = [tuple(['consumidor'] + list(x) + [1]) for x in df[['mensagem_show', 'data_manifestacao_show', 'Reclamacao']].to_numpy()]

psycopg2.extras.execute_batch(cur, reclamacoes_plataforma_query, reclamacoes_plataforma_values, page_size=page_size)
psycopg2.extras.execute_batch(cur, historico_query, historico_values, page_size=page_size)

toc = time.perf_counter(); print(f"FOURTH PASS done! {toc - tic:0.4f}")

#con.commit()
#con.close()

print("committed")
