import gdown

url = 'https://drive.google.com/uc?id=1xnZgYPBLLWokF7RCgaG7H9QrDAwfooib'
output = '/indexer/indices-sample/relatos/relatos0-100000.csv'
gdown.download(url, output, quiet=False)

url = 'https://drive.google.com/uc?id=1Gcs3N0tD_1wcTNT2iXe2LV2zqZJyBHcu'
output = '/indexer/indices-sample/relatos/relatos100000-200000.csv'
gdown.download(url, output, quiet=False)

url = 'https://drive.google.com/uc?id=13YesccfnmtTOnPQjPZHo-fhiasUXOoZD'
output = '/indexer/indices-sample/relatos/relatos200000-300000.csv'
gdown.download(url, output, quiet=False)

url = 'https://drive.google.com/uc?id=1HI2o8oNeoY4om_Ve7NvjX6Eg23aoGKm7'
output = '/indexer/indices-sample/relatos/relatos300000-378574.csv'
gdown.download(url, output, quiet=False)