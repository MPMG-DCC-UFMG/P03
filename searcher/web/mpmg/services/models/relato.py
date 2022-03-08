from mpmg.services.models.elastic_model import ElasticModel


class Relato(ElasticModel):
    index_name = 'relatos'

    def __init__(self, **kwargs):
        index_name = Relato.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type', 'score']
        index_fields = [
            'nome',
            'data',
            'estado',
            'cidade',
            'conteudo',
            'embedding_vector',
            'resposta',
            'status'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    