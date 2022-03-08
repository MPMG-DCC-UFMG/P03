import argparse
from indexer import Indexer, list_files, isfile

parser = argparse.ArgumentParser(description='Indexa arquivos csv no ES dado.')
parser.add_argument("-strategy", choices=['simple', 'parallel'], default="simple", help="Strategy for indexing the data: [simple] or [parallel]")
parser.add_argument("-index", help="Index", required=True)
parser.add_argument("-f", nargs='+', help="List of csv files to index")
parser.add_argument("-d", nargs='+', help="List of directories which all files will be indexed")
parser.add_argument("-t", help="Threadpool size to use for the bulk requests")
parser.add_argument("-elastic_address", default="es:9200", help="Elasticsearch address. Format: <ip>:<port>")
parser.add_argument("-username", nargs='?', help="Username to access elasticsearch if needed.")
parser.add_argument("-password", nargs='?', help="Password to access elasticsearch if needed.")
parser.add_argument("-model_path", default="neuralmind/bert-base-portuguese-cased", help="Model Path")
args = vars(parser.parse_args()) 

index = args["index"]



csv_indexer = Indexer(elastic_address=args['elastic_address'], model_path=args['model_path'], username=args['username'], password=args['password'])
csv_indexer.table_indexer(index)
