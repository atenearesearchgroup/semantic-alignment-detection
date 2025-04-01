from typing import List

import nltk
import sentence_generator.util as util
import pandas as pd
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromAttributes(AbstractSentenceGenerator):
    def __init__(self, attributes, model):
        self.attributes = attributes
        self.language_model = model

        self.verb_phrase = 'has'  # can be changed later, it seems to work fine as of now

        # TODO : Keep only one format either sentences list or 'attributes'  dataframe
        self.sentences = []
        self.attributes_description = pd.DataFrame(columns=['class', 'attribute', 'sentence'])
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    def get_attributes(self):
        return self.attributes_description

    def combine_pos_tags(self, words, splitted_words, pos_tags):
        tags = {}

        # Split the compound word into its constituent parts based on camel case
        for word in words:
            word = word.split(":")[0]
            compound_parts = util.split_camel_case(word)

            # Initialize a list to store POS tags for the compound parts
            compound_pos_tags = []

            # Iterate through the compound parts
            for part in compound_parts:
                # Find the index of the part in the words list
                index = splitted_words.index(part)  # Convert to lowercase for matching
                # Get the POS tag for the part and add it to the compound_pos_tags list
                compound_pos_tags.append(pos_tags[index][1])

            # Combine the POS tags of individual parts into a single tag for the compound word
            combined_pos_tag = '+'.join(compound_pos_tags)
            tags[word] = combined_pos_tag

        return tags

    def perform_pos_tagging(self, words):
        # Tokenize the text into words
        # words = word_tokenize(text)

        splitted_words = []
        for word in words:
            # To remove datatype information and keep only attribute name
            compound_parts = util.split_camel_case(word.split(":")[0])
            splitted_words.extend(compound_parts)

        # Perform POS tagging
        pos_tags = nltk.pos_tag(splitted_words)

        # Get POS tag for the compound word by combining POS tags of individual parts
        compound_pos_tags = self.combine_pos_tags(words, splitted_words, pos_tags)

        # Print the POS tags
        # print(compound_pos_tags)
        return compound_pos_tags

    def generate_sentences(self):
        # TODO : For boolean attributes, replace 'has' with 'can have'/can be.
        # Add support to store and handle type of the attribute.
        for class_name, attributes_list in self.attributes.items():
            # From attributes:
            pos_tags = self.perform_pos_tagging(attributes_list)

            # Case 1: Formation of ‘‘has’’ sentences (object name has attribute)
            # examples : balance in account, name address in Bike station
            # Filter words and their POS tags based on desired POS tags
            filtered_dict = {word: pos_tag for word, pos_tag in pos_tags.items() if not util.contains_verb(pos_tag)}

            attributes = []
            for word, pos_tag in filtered_dict.items():
                attributes.append(word)

            # Case 2: Formation with verbs
            filtered_dict = {word: pos_tag for word, pos_tag in pos_tags.items() if util.contains_verb(pos_tag)}

            for word, pos_tag in filtered_dict.items():
                parts = pos_tag.split("+")

                # Case 2.1 : only verb, add class name as suffix
                # examples : completed in Campaign class
                if len(parts) == 1:
                    # lemmatize the verb remove 'ed'
                    attr_name = word + " " + class_name
                    attributes.append(attr_name)

                else:
                    word_parts = util.split_camel_case(word)
                    # Case 2.2 : if verb has noun phrase on left, verb is on right
                    if util.contains_verb(parts[1]):
                        # lemmatize the verb remove 'ed'
                        attr_name = word_parts[1] + " " + word_parts[0]
                        attributes.append(attr_name)

                    # Case 2.3 : if verb has noun phrase on right, verb is on left
                    # examples : estimatedCost in Campaign class,
                    elif util.contains_verb(parts[0]):
                        # lemmatize the verb remove 'ed'
                        attr_name = ""
                        for w in word_parts:
                            attr_name += " " + w
                        # attr_name = word_parts[0] + " " + word_parts[1]
                        attributes.append(attr_name)

            # if len(attributes) > 0:
            #     # With aggregation
            #     sentence = util.format_concept(class_name) + " " + self.verb_phrase + " "
            #     if len(attributes) == 1:
            #         sentence = sentence + util.format_concept(attributes[0])
            #
            #     else:
            #         for i, attribute in enumerate(attributes):
            #             if i < len(attributes) - 2:
            #                 sentence = sentence + util.format_concept(attribute) + ", "
            #             elif i == len(attributes) - 2:
            #                 sentence = sentence + util.format_concept(attribute) + " "
            #             elif i == len(attributes) - 1:
            #                 sentence = sentence + "and " + util.format_concept(attribute)
            #
            #     self.attributes_description.loc[len(self.attributes_description)] = [class_name, attributes, sentence]
            #     self.sentences.append(sentence)

            # Without aggregation
            for attribute in attributes:
                formatted_class_name = util.split_concept(class_name)
                formatted_attribute = util.split_concept(attribute)
                sentence = util.format_concept(class_name, self.language_model) + " " + self.verb_phrase + " " + util.format_concept(
                    attribute, self.language_model)
                self.attributes_description.loc[len(self.attributes_description)] = [formatted_class_name,
                                                                                     formatted_attribute, sentence]
                self.sentences.append(sentence)

            # With aggregation
            # sentence = sentence[:-2] + "."
            print(self.sentences)


factory_attributes = {
    'Factory': ["city"],
    "Machine": ['speed', 'capacity'],
    "Piece": ['width', "height", "depth"],
    "Worker": ['id', 'name', 'salary']
}

city_attributes = {
    # 'Campaign': ["estimatedCost", "overallCost", "completed"],
    "City": ['name'],
    "Neighbourhood": ['name', "aqi"],
    "AirQualitySensor": ['CO', 'O3', 'SO2', 'NO2', 'others'],
    "Display": ['size', 'resolution']
}

bank_attributes = {
    "Customer": [],
    "Account": ['balance']
}

transportation_attributes = {
    "SustainableCity": ['name', 'country'],
    "BikeStation": ['name', 'address', 'spots'],
    "User": ['id', 'name', 'creditcard'],
    "Rental": ['startDate', 'endDate'],
    "Bike": ['code', 'priceHour']
}

library_attributes = {
    'BookCopy': ["barcode:string", "onReserve"],
    "Loan": ['startDate', 'endDate'],
    "Member": ['name', "email"],
    "Book": ['title'],
    "BookCategory": ["name"],
    "LoanPeriod": ["duration"],
    "MemberCategory": ["name", "maxNumberBooks"]
}

# sfa = SentenceFromAttributes(library_attributes)
# print(sfa.attributes_description)
