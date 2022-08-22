# P03 - Preparação de Dados para o Classificador de Assuntos

Extrai os relatos e seus respectivos rótulos da cópia do banco disponibilizado pelo MPMG e gera diferentes combinações de partições para treinamento, teste e validação.

# Como executar

Adicionar as credenciais para acesso à cópia do banco do MPMG no arquivo picklenizer.py linha 13.
```shell script
pip install pyhive sklearn

python3 picklenizer.py \[diretório de saída\]
```
Exemplo
```shell script
python3 svm.py /tmp/PROCON/
```
