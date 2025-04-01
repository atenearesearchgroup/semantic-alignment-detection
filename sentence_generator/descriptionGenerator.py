import os

import pandas as pd

from sentence_generator.SentenceFromEnums import SentenceFromEnums
from sentence_generator.sentenceFromAttributes import SentenceFromAttributes
from sentence_generator.sentenceFromAssociations import SentenceFromAssociations
from sentence_generator.sentenceFromCompositions import SentenceFromCompositions
from sentence_generator.sentenceFromAggregations import SentenceFromAggregation
from sentence_generator.sentenceFromInheritance import SentenceFromInheritance
from sentence_generator.postProcessor import PostProcessor
from domain_converter.xmlReader import parse_domain_model

model_path = "D:\\Thesis\\modelling-assistant\\tests\\\domain-models\\"


processed_models_path = "processed_models\\"


class DescriptionGenerator:
    def __init__(self, domain_name, language_model):
        self.domain_name = domain_name
        self.language_model = language_model

        attributes, associations, compositions, aggregations, inheritance, enums = self.read_model()
        self.generator_from_attributes = SentenceFromAttributes(attributes, language_model)
        self.generator_from_associations = SentenceFromAssociations(associations, language_model)
        self.generator_from_compositions = SentenceFromCompositions(compositions)
        self.generator_from_aggregations = SentenceFromAggregation(aggregations, language_model)
        self.generator_from_inheritance = SentenceFromInheritance(inheritance)
        self.generator_from_enums = SentenceFromEnums(enums, language_model)
        self.post_processor = PostProcessor()

        # TODO : Keep only one format either description string or 'attributes' and 'relationships' dataframes
        self.description = ''
        self.attributes_description = pd.DataFrame(columns=['class', 'attribute', 'sentence'])
        self.associations = pd.DataFrame(
            columns=['source', 'target', 'role', 'source_role', 'multiplicity', 'sentence'])
        self.compositions = pd.DataFrame(columns=['source', 'target', 'role', 'source_role', 'sentence'])
        self.aggregations = pd.DataFrame(
            columns=['source', 'target', 'role', 'source_role', 'multiplicity', 'sentence'])
        self.inheritance = pd.DataFrame(columns=['source', 'target', 'role', 'source_role', 'sentence'])
        self.enums = pd.DataFrame(columns=['enum', 'enum_member', 'sentence'])
        self.generate_description()

    def get_description(self):
        return self.description

    def get_attributes(self):
        return self.attributes_description

    def get_associations(self):
        return self.associations

    def get_compositions(self):
        return self.compositions

    def get_aggregations(self):
        return self.aggregations

    def get_inheritance(self):
        return self.inheritance

    def get_enums(self):
        return self.enums

    def read_model(self):

        # TODO below code was used to read domain diagram from txt file
        file_path = model_path + processed_models_path + self.domain_name
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()

            local_vars = {}

            exec(content, local_vars)

            return (local_vars.get('class_attributes', {}), local_vars.get('associations', []),
                    local_vars.get('compositions', []), local_vars.get('aggregations', []),
                    local_vars.get('inheritance', []), local_vars.get('enums', {}))
        else:
            print(f"File {file_path} does not exist. Read cdm model")

            # Code to read domain diagram in .cdm format
            class_attributes, associations, compositions, aggregations, inheritance, enums = parse_domain_model(
                model_path + "cdm-models\\" + self.domain_name + ".cdm")

            return class_attributes, associations, compositions, aggregations, inheritance, enums

    def generate_description(self):
        processed_sentences = []

        # From Attributes
        for index, row in self.generator_from_attributes.get_attributes().iterrows():
            # sentence = self.post_processor.morphological_process(sentence)
            sentence = row['sentence'].replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.attributes_description.loc[len(self.attributes_description)] = [row['class'], row['attribute'],
                                                                                 sentence]
            processed_sentences.append(sentence)

        # From Associations
        for index, row in self.generator_from_associations.get_relationships().iterrows():
            # Since we are handling singular/plural thing while generating the sentences, this is not required here.
            # sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = row['sentence'].replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.associations.loc[len(self.associations)] = [row['source'], row['target'], row['role'],
                                                             row['source_role'], row['multiplicity'],
                                                             sentence]
            processed_sentences.append(sentence)

        # From Compositions
        for index, row in self.generator_from_compositions.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.compositions.loc[len(self.compositions)] = [row['parent_class'], row['child_class'], row['role'],
                                                             row['source_role'],
                                                             sentence]
            processed_sentences.append(sentence)

        # From Aggregations
        for index, row in self.generator_from_aggregations.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.aggregations.loc[len(self.aggregations)] = [row['parent_class'], row['child_class'], row['role'],
                                                             row['source_role'], row['multiplicity'],
                                                             sentence]
            processed_sentences.append(sentence)

        # From Inheritance
        for index, row in self.generator_from_inheritance.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.inheritance.loc[len(self.inheritance)] = [row['parent_class'], row['child_class'], None, None,
                                                           sentence]
            processed_sentences.append(sentence)

        # From Enum
        for index, row in self.generator_from_enums.get_enums().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.enums.loc[len(self.enums)] = [row['enum'], row['enum_member'], sentence]
            processed_sentences.append(sentence)

        sentences = processed_sentences

        final_sentence = ''.join([s + '. ' for s in sentences])
        self.description = final_sentence
        print(final_sentence)

# dec = DescriptionGenerator('factory')
# print(dec.get_attributes())
