import pandas as pd
import glob
import os.path
import sys
dir = sys.argv[1]
allfiles = os.listdir(dir)
files = [fname for fname in allfiles if fname.endswith('.xlsx')]
print(files)
if not dir.endswith('/'):
	dir = dir + '/'
for file in files:
	# Read and store content
	# of an excel file 
	read_file = pd.read_excel(dir + file, engine='openpyxl', encoding="utf-8")
	 
	#read_file = read_file.iloc[: , 1:]
	read_file = read_file.rename(columns={read_file.columns[0]:'id', 'Relato':'conteudo'})
	names = {}
	for col in read_file.columns:
		names[col] = col.lower()
	read_file = read_file.rename(columns=names)

	# Write the dataframe object
	# into csv file
	read_file.to_csv (dir + file.replace('.xlsx','.csv'),
					  index = None,sep='\t',
					  header=True, encoding="utf-8")
    