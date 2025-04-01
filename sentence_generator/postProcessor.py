import nltk
from nltk.corpus import wordnet
import re
import sentence_generator.constants as constants
import spacy
import sentence_generator.util as util
import stanza


class PostProcessor:
    def __init__(self):
        custom_tokenizer_patterns = [
            (r'(\S+)\+pl', r'\1+pl')
        ]

        # Initialize Stanza pipeline with custom tokenizer patterns
        self.nlp = stanza.Pipeline(lang='en', tokenize_pretokenized=True, tokenize_no_ssplit=True,
                                   tokenize_custom_patterns=custom_tokenizer_patterns)

    def conjugate_verb(self, base_verb):
        if base_verb.endswith(('o', 's', 'x', 'z', 'ch', 'sh')):
            return base_verb + 'es'
        elif base_verb.endswith('y') and base_verb[-2] not in 'aeiou':
            return base_verb[:-1] + 'ies'
        elif base_verb.endswith('y'):
            return base_verb + 's'
        else:
            return base_verb + 's'

    def morphological_process(self, text):
        words = re.split(r' ', text)

        result = self.nlp(text).sentences[0]

        for token in result.tokens:
            if "+pl" in token.text:
                conj = find_conjugate(result, token)
                if conj is not None:
                    noun = related_noun(result, conj)
                    if noun is not None:
                        features = noun.feats.split("|")
                        for feature in features:
                            if "Number" in feature:
                                number = feature.split("=")
                                if "Plur" not in number[1]:
                                    plural = util.get_plural(noun.text)
                                    words[noun.id - 1] = plural
                                break

                else:
                    noun = related_noun(result, token)
                    if noun is not None:
                        features = noun.feats.split("|")
                        for feature in features:
                            if "Number" in feature:
                                number = feature.split("=")
                                if "Plur" not in number[1]:
                                    plural = util.get_plural(noun.text)
                                    words[noun.id - 1] = plural
                                break

            elif "+sg" in token.text:
                noun = related_noun(result, token)
                if noun is not None:
                    features = noun.feats.split("|")
                    for feature in features:
                        if "Number" in feature:
                            number = feature.split("=")
                            if "Sing" not in number[1]:
                                plural = util.get_singular(noun.text)
                                words[noun.id - 1] = plural
                            break

        # ToDo Revisit
        # elif tag[0][1] in verb_tags:
        #     # Verb to noun agreement
        #     if tag[0][1] in ['VB', 'VBZ', 'VBP']:
        #         # Present tense
        #         new_word = wordnet.morphy(word)
        #         if new_word:
        #             print(new_word)
        #             words[i] = conjugate_verb(new_word)
        #         else:
        #             print("error")
        #     elif tag[0][1] in ['VBN']:
        #         # Passive form
        #         new_word = wordnet.morphy(word)
        #         print(new_word)

        # print(words)

        return ' '.join(words)

    # Aggregator : Discuss the requirement

    # ToDo Semantic analyser


def related_noun(result, token):
    for dependency in result.dependencies:
        if dependency[0].id == token.id[0] and dependency[2].xpos in constants.noun_tags:
            return dependency[2]
        elif dependency[2].id == token.id[0] and dependency[0].xpos in constants.noun_tags:
            return dependency[0]

    return None


def find_token_with_id(tokens, id):
    for token in tokens:
        if token.id[0] == id:
            return token


def find_conjugate(result, token):
    for dependency in result.dependencies:
        print()
        if dependency[0].id == token.id[0] and dependency[1] == 'conj':
            return find_token_with_id(result.tokens, dependency[2].id)
        elif dependency[2].id == token.id[0] and dependency[1] == 'conj':
            return find_token_with_id(result.tokens, dependency[0].id)

    return None

# pp = PostProcessor()
# pp.morphological_process(
#     " each Bike Station is in exactly one+sg Sustainable City")
