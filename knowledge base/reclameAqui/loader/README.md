# P03 - ReclameAqui Loader

Carrega para a Base de Conhecimento os dados extraídos pelo parser.py.

# Como executar

Adicionar as credenciais para acesso ao banco de dados da Base de Conhecimento no arquivo credentials.int.

> pip install psycopg2

> python3 loader.py \[arquivo de saída do parser.py\]

Exemplo

> python3 loader.py \_datalake\_ufmg\_crawler\_webcrawlerc01\_reclameaqui\_1\_data\_raw\_pages\_.csv.gz
