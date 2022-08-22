# P03 - Classificador de Assuntos com SVM

Treina um classificador SVM para os assuntos utilizando os dados gerados pelo picklenizer.py

# Como executar

```shell script
pip install pandas sklearn spacy

python3 svm.py \[diretório de saída do picklenizer.py\]
```
Exemplo
```shell script
python3 svm.py /tmp/PROCON/
```
Otimização para processadores Intel
```shell script
pip install scikit-learn-intelex

python3 -m sklearnex picklenizer.py \[diretório de saída\]
```

