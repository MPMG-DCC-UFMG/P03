# ReclameAqui parser

# Author: Elves Rodrigues

# Modified by: Felipe Costa

import csv
import ctypes
import gzip
import json
import sys
from glob import glob
from tqdm import tqdm
from pathlib import Path

csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

csv_fields = [
    'id',
    'data_criacao',
    'titulo',
    'cidade',
    'estado',
    'tipo_problema',
    'resolvido:bool',
    'conteudo',
    'tipo_postagem',
    'ordem_da_interacao',
    'tipo_interacao',
    'id_pai',
    'nome_completo_empresa',
    'nome_curto_empresa',
    'site_empresa',
    'categoria_empresa',
]

NEW_CSV_FILEPATH = sys.argv[1].replace('/','_') + '.csv.gz'

NEW_FILE = gzip.open(NEW_CSV_FILEPATH, 'wt', encoding='utf-8')
NEW_CSV_WRITER = csv.DictWriter(NEW_FILE, csv_fields)
NEW_CSV_WRITER.writeheader()

SPLIT_TAG_INIT = '<script id="__NEXT_DATA__" type="application/json">'
SPLIT_TAG_END = '</script>'

def jsonfy(path: str) -> dict:
    with open(path) as f:
        page_body = f.read()
        if SPLIT_TAG_INIT in page_body:
            return json.loads(page_body.split(SPLIT_TAG_INIT)[-1].split(SPLIT_TAG_END)[0])['props']['pageProps']
        return {}

def create_row(complaint: dict, company: dict, problem_type: str, created_at: str, interaction: dict = None, iteraction_order: int = None, id_pai: str = None):
    categories = company['categories']
    data = {
        'data_criacao': created_at[:10],
        'titulo': complaint.get('title', '').replace('<br />', '\n'),
        'cidade': complaint.get('userCity', ''),
        'estado': complaint.get('userState', ''),
        'resolvido:bool': complaint.get('solved'),
        'tipo_problema': problem_type if problem_type else None, # ???
        'nome_completo_empresa': company['companyName'],
        'nome_curto_empresa': company['shortname'],
        'site_empresa': company['urls'][0].get('path', '') if len(company['urls']) else '',
        'categoria_empresa': [cat['name'] for cat in categories]

    }

    if interaction is None: 
        data['id'] = complaint['id']
        data['id_pai'] = complaint['id']
        data['tipo_interacao'] =  'COMPLAINT'
        data['ordem_da_interacao'] = 0
        data['conteudo'] = complaint.get('description', '').replace('<br />', '\n')
        data['tipo_postagem'] = 'complaint'
            
    else:
        data['id'] = interaction['id']
        data['id_pai'] = id_pai
        data['tipo_interacao'] = interaction['type']
        data['ordem_da_interacao'] = iteraction_order
        data['conteudo'] = interaction['message'].replace('<br />', '\n')
        data['tipo_postagem'] = 'interaction'

    return data

if __name__ == '__main__':
    raw_page_path_rgx = sys.argv[1]
    
    paths = Path(raw_page_path_rgx).glob('**/*.html',)

    num_complaints = 0

    for raw_page_path in paths:
        extracted_json = jsonfy(raw_page_path)

        if 'complaint' in extracted_json and len(extracted_json['complaint']['interactions']):

            complaint = extracted_json['complaint']
            company = extracted_json['company']

            problem_type =  extracted_json['problemType']['name'] if extracted_json['problemType'] else complaint.get('otherProblemType', '')
            
            data = create_row(complaint, company, problem_type, complaint['created']) 
            complaint_id = data['id']

            NEW_CSV_WRITER.writerow(data)

            for idx, interaction in enumerate(extracted_json['complaint']['interactions'], 1):
                interaction = create_row(complaint, company, problem_type, interaction['created'], interaction, idx, complaint_id)
                NEW_CSV_WRITER.writerow(interaction)

            num_complaints += 1

    NEW_FILE.close()
