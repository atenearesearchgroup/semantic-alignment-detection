from typing import List

from pandas import DataFrame

import sentence_generator.util as util
import pandas as pd
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromInheritance(AbstractSentenceGenerator):
    def __init__(self, inheritance):
        self.inheritance = inheritance
        self.inheritance_phrase = 'is a type of'

        # TODO : Keep only one format either sentences list or 'relationships'  dataframe
        self.sentences = []
        self.inheritance_result = pd.DataFrame(columns=['parent_class', 'child_class', 'sentence'])

        self.generate_sentences()

    def get_sentences(self) -> DataFrame:
        return self.inheritance_result

    def generate_sentences(self):
        # TODO handle the case where role name is provided and it is not same as class name
        for relation in self.inheritance:
            parent_class_name = util.format_class_name(relation['parent_class'])
            child_classes = relation['child_classes']

            for child_class_name in child_classes:
                part_of_sentence = ''
                part_of_sentence += util.format_class_name(child_class_name) + " "
                part_of_sentence += self.inheritance_phrase + " "
                part_of_sentence += parent_class_name

                self.sentences.append(part_of_sentence)
                self.inheritance_result.loc[len(self.inheritance_result)] = [parent_class_name, util.format_class_name(child_class_name),
                                                                             part_of_sentence]


car_maintenance_inheritance = [
    {
        'parent_class': 'Garage',
        'child_classes': ['OfficialGarage']
    }
]

production_cell_inheritance = [
{
    'parent_class': 'Unit',
    'child_classes': ['ProcessingUnit', 'TransportUnit']
},
{
    'parent_class': 'ProcessingUnit',
    'child_classes': ['Press', 'Laser']
},
{
    'parent_class': 'TransportUnit',
    'child_classes': ['ConveyorBelt', 'RobotArm']
}
]

# sfi = SentenceFromInheritance(car_maintenance_inheritance)
# sfi.get_sentences()
