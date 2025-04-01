from typing import List

from pandas import DataFrame

import sentence_generator.util as util
import pandas as pd
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromCompositions(AbstractSentenceGenerator):
    def __init__(self, compositions):
        self.compositions = compositions
        self.composition_phrase = 'is made up of'

        # TODO : Keep only one format either sentences list or 'relationships'  dataframe
        self.sentences = []
        self.compositions_result = pd.DataFrame(
            columns=['parent_class', 'child_class', 'role', 'source_role', 'sentence'])

        self.generate_sentences()

    def get_sentences(self) -> DataFrame:
        return self.compositions_result

    def generate_sentences(self):
        # TODO handle the case where role name is provided and it is not same as class name
        for composition in self.compositions:
            parent_class_name = util.format_class_name(composition['parent_class'])
            child_class_name = util.format_class_name(composition['child_class'])
            cardinality = composition['cardinality']

            if len(cardinality) == 0:
                cardinality = "0..*"

            if 'role' in composition:
                role = util.format_role_name(composition['role'])
            else:
                role = ''

            part_of_sentence = ''
            part_of_sentence += "Each " + parent_class_name + " "
            part_of_sentence += self.composition_phrase + " "

            if not util.is_singular(cardinality):
                part_of_sentence += util.get_plural(child_class_name)
            else:
                part_of_sentence += child_class_name
            self.sentences.append(part_of_sentence)
            self.compositions_result.loc[len(self.compositions_result)] = [parent_class_name, child_class_name, role,
                                                                           None,
                                                                           part_of_sentence]


car_compositions = [
    {
        'parent_class': 'Car',
        'child_class': 'Service',
        'cardinality': '*',
        'role': 'services'
    }
]

factory_compositions = [
    {
        'parent_class': 'Factory',
        'child_class': 'Machine',
        'cardinality': '1..*',
        'role': ''
    }
]

production_compositions = [
    {
        'parent_class': 'ProductionCell',
        'child_class': 'Unit',
        'cardinality': '0..*',
        'role': 'units',
    }

]

# sfc = SentenceFromCompositions(production_compositions)
# sfc.get_sentences()
