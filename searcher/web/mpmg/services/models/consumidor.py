from mpmg.services.models.elastic_model import ElasticModel


class Consumidor(ElasticModel):
    index_name = 'consumidor'

    def __init__(self, **kwargs):
        index_name = Consumidor.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type', 'score']
        index_fields = [
            'data',
            'conteudo',
            'embedding_vector',
            'autor'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    