# P03 - Classificador de Assuntos com BERT

Treina um classificador BERT para os assuntos utilizando os dados gerados pelo picklenizer.py

# Como executar

Para esse classificador utilizamos o TeCBech disponível no repositório https://github.com/celsofranssa/TeCBench

Seguir as instruções do diretório e depois executar:

```shell script
  python main.py tasks=[fit,predict,eval] \
                 model=BERT \
                 data=procon \
                 data.name=procon \
                 data.dir=\[diretório de saída do picklenizer.py\] \
                 data.folds=[0,1,2,3,4,5,6,7,8,9] \
                 data.max\_length=256 \
                 data.num\_classes=6 \
                 data.batch\_size=32 \
                 data.num\_workers=10
```
