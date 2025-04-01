import re

import inflect

import sentence_generator.constants as constants


def get_cardinality(cardinality):
    if is_singular(cardinality):
        return constants.singular_cardinality_to_article_map[cardinality]
    else:
        return constants.multiple_cardinality_to_article_map[cardinality]


def is_singular(cardinality):
    return ".." not in cardinality and "*" not in cardinality


def contains_verb(tag):
    return any(substring in tag for substring in constants.verb_tags)


def get_appropriate_article(attribute, language_model):
    doc = language_model(attribute)
    if 'Plur' in doc[0].morph.get("Number"):
        return ""
    elif attribute[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return 'an'
    else:
        return 'a'


def get_pos_tag(words, language_model):
    doc = language_model(words)
    pos_tags = []

    for token in doc:
        pair = (token.text, token.tag_)
        pos_tags.append(pair)

    return pos_tags


# Function to split compound words written in camel case
def split_camel_case(word):
    # Use regular expression to split camelCase
    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)(?![a-z0-9])(?![A-Z0-9])', word)
    return parts


# Similar to format_concept but doesn't add an article
def split_concept(concept):
    digit_pattern = re.compile(r'\d')

    if bool(digit_pattern.search(concept)):
        return concept

    if bool(re.match(r'^[A-Z]+$', concept)):
        return concept

    splitted_concept = split_camel_case(concept)
    return " ".join([item.lower() for item in splitted_concept])


def format_concept(concept, language_model):
    digit_pattern = re.compile(r'\d')
    article = get_appropriate_article(concept, language_model)

    if bool(digit_pattern.search(concept)):
        return article + " " + concept

    if bool(re.match(r'^[A-Z]+$', concept)):
        return article + " " + concept

    splitted_concept = split_camel_case(concept)
    return article + " " + " ".join([item.lower() for item in splitted_concept])


def format_role_name(role):
    splitted_concept = split_camel_case(role)
    return " ".join([item.lower() for item in splitted_concept])


def format_class_name(class_name):
    splitted_concept = split_camel_case(class_name)
    return " ".join([item.lower() for item in splitted_concept])


def get_plural(word):
    """Get the plural form of a word using the inflect library."""
    p = inflect.engine()
    if p.singular_noun(word):
        return word
    return p.plural(word)


def get_singular(word):
    p = inflect.engine()
    singular_form = p.singular_noun(word)
    return singular_form
