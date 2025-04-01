from typing import List

import pandas as pd
from pandas import DataFrame

from sentence_generator import util
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator
from sentence_generator.sentenceFromAssociations import get_role_and_cardinality


class SentenceFromAggregation(AbstractSentenceGenerator):
    def __init__(self, aggregations, model):
        self.aggregations = aggregations
        self.language_model = model
        # TODO : Keep only one format either sentences list or 'relationships'  dataframe
        self.sentences = []
        self.aggregation_result = pd.DataFrame(columns=['parent_class', 'child_class', 'role', 'source_role', 'sentence'])
        self.aggregation_phrase = "has"
        self.generate_sentences()

    def get_sentences(self) -> DataFrame:
        return self.aggregation_result

    # TODO This is same as associations,  keep only one method at common place

    def generate_sentences(self):
        # With role name
        for aggregation in self.aggregations:
            # TODO below code generates two sentences for each aggregation, describing each end of association in one
            #  sentence >>>>
            parent_class = aggregation['parent_class']
            child_class = aggregation['child_class']
            role = aggregation['role']
            cardinality = aggregation['cardinality']

            # Removes "Each" from start of the sentence when cardinality is too many or not there.
            part_of_sentence = ''
            if cardinality == '':
                part_of_sentence += "A "
            elif util.is_singular(cardinality):
                part_of_sentence += "Each "
            else:
                part_of_sentence += "A "

            part_of_sentence += (util.format_class_name(parent_class)
                                 + " " +
                                 get_role_and_cardinality(role, cardinality, child_class, self.language_model))

            self.sentences.append(part_of_sentence)
            self.aggregation_result.loc[len(self.aggregation_result)] = [util.split_concept(parent_class),
                                                                         util.split_concept(child_class),
                                                                         role,
                                                                         None,
                                                                         part_of_sentence]

        # TODO see if we really need a sentence to describe other end of this aggregation i.e.
        # <<<<<

        # TODO below code generates only one sentence for each association:
        # part_of_sentence = ''
        # part_of_sentence += "Each " + util.format_class_name(
        #     association['class1']) + " " + self.get_role_and_cardinality(
        #     association['role_class2'],
        #     association[
        #         'cardinality_class2'], association['class2']) + " "
        #
        # part_of_sentence += "while " + "each " + util.format_class_name(
        #     association['class2']) + " " + self.get_role_and_cardinality(
        #     association['role_class1'], association['cardinality_class1'], association['class1'])
        # self.sentences.append(part_of_sentence)

        print(self.sentences)


aggregations = [
    {
        'parent_class': 'MemberCategory',
        'child_class': 'Member',
        'cardinality': '0..*',
        'role': 'members'
    },
    {
        'parent_class': 'Book',
        'child_class': 'BookCopy',
        'cardinality': '0..*',
        'role': 'copies'
    },
    {
        'parent_class': 'BookCategory',
        'child_class': 'Book',
        'cardinality': '0..*',
        'role': 'books'
    }
]

# sfa = SentenceFromAggregation(aggregations)
# print(sfa.get_sentences())
