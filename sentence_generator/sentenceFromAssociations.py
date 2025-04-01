import re
from typing import List

import nltk
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator
import sentence_generator.util as util
import spacy
import pandas as pd


# Associations
# Template : o1 cardinality -> o1 name -> association name -> o2 cardinality -> o2 name
# Template: o1 cardinality -> o1 name/role -> "can have"/"can be associated to" -> o2 cardinality -> o2 name/roles
# association_phrase = "can be associated to"
# association_phrase = "is associated to

# Rules for "need of auxillary verb":
# 1. Auxillary verb + main verb :  isOperatedBy : no changes needed
# 2. Verb as adjective.modifier : bikesParked
# 3. Main verb with morph analysis Present/past/future tense : parkedIn : Decide on is/are/was/were
# TODO : Check if multiple tense conditions needs to be checked or will 'has' work in every case
# 4. Main verb infinitive form : drop : Go with 'has'

def get_main_and_auxilary_verb(result):
    main_verb = None
    auxillary_verb = None
    for token in result:
        if token.pos_ == 'VERB' and util.contains_verb(token.tag_):
            main_verb = token
        elif token.pos_ == 'AUX':
            auxillary_verb = token

    return main_verb, auxillary_verb


def ends_with_preposition(result):
    last_token = result[len(result) - 1]
    return last_token.pos_ == "ADP"


def get_present_form_of_verb(main_verb, auxillary_verb):
    if auxillary_verb is not None:
        return main_verb.text
    else:
        base_form = main_verb.lemma_
        if base_form.endswith("y") and not base_form[-2] in "aeiou":
            # Convert verbs like "fly" -> "flies"
            return base_form[:-1] + "ies"
        elif (base_form.endswith("s") or base_form.endswith("sh") or
              base_form.endswith("ch") or base_form.endswith("x") or
              base_form.endswith("z")):
            # Add "es" to verbs like "pass" -> "passes"
            return base_form + "es"
        else:
            # Add "s" for regular verbs
            return base_form + "s"


def get_role_and_cardinality(role, cardinality, associated_class, language_model):
    verb_forms_with_auxillary_verb = ['Inf', 'Part']

    # Case 1: Role name is not provided
    # e.g. City and Neighborhood in smart city
    # TODO : Discuss how to handle such cases where role is not provided
    if len(role) == 0:
        if util.is_singular(cardinality):
            return "has " + util.format_class_name(associated_class)
        else:
            phrase = "can have "
            ass_class = " ".join([item.lower() for item in util.split_camel_case(associated_class)])
            result = language_model(ass_class)
            for doc in result:
                if doc.dep_ == 'ROOT':
                    phrase += util.get_plural(doc.text) + " "
                else:
                    phrase += doc.text + " "

            return phrase

    words = util.split_camel_case(role)

    # Sometimes Role has 'my' word in it, it is not a usual practice. Remove 'my' if its there.
    if "my" in words:
        words.remove("my")
        role = role.replace("my", "")

    pos_tag = nltk.pos_tag(words)
    result = language_model(" ".join(words))

    auxillary_verb_needed = True
    main_verb, auxillary_verb = get_main_and_auxilary_verb(result)

    # Case 2: role name is provided
    # TODO First condition is redundant when second condition is there, can be removed at the end
    if main_verb is not None and auxillary_verb is not None:
        auxillary_verb_needed = False
    elif auxillary_verb is not None:
        auxillary_verb_needed = False
    elif main_verb is not None:
        if main_verb.has_morph():
            verb_form = main_verb.morph.get('VerbForm', [])
            if any(elem in verb_forms_with_auxillary_verb for elem in verb_form):
                auxillary_verb_needed = True
            else:
                auxillary_verb_needed = False
        else:
            auxillary_verb_needed = True
    else:
        auxillary_verb_needed = True

    # Case 2.1: Main verb + auxiliary verb
    if not auxillary_verb_needed:
        phrase = ''

        if main_verb is not None:
            main_verb_in_present_tense = get_present_form_of_verb(main_verb, auxillary_verb)
            formatted_role_name = util.format_role_name(role).split(" ")
            for elem in formatted_role_name:
                if elem == main_verb.text:
                    phrase += main_verb_in_present_tense + " "
                else:
                    phrase += elem + " "
        else:
            phrase += util.format_role_name(role)
        if util.is_singular(cardinality):
            phrase += util.get_appropriate_article(associated_class, language_model) + " " + util.format_class_name(
                associated_class)
        else:
            ass_class = " ".join([item.lower() for item in util.split_camel_case(associated_class)])
            result = language_model(ass_class)
            for doc in result:
                if doc.dep_ == 'ROOT':
                    phrase += util.get_plural(doc.text) + " "
                else:
                    phrase += doc.text + " "

        return phrase

    # Case 2: auxillary verb needed, but role contains class name
    elif associated_class.lower() in role.lower():

        if util.is_singular(cardinality):
            phrase = "has "
            singular_form = util.get_singular(role)
            if isinstance(singular_form, bool):
                singular_form = role
            phrase += util.get_appropriate_article(singular_form, language_model) + " " + util.format_role_name(
                singular_form)

        else:
            # TODO : Handle the case where cardinality is 'many' and role name has associated class but it is not plural
            temp = ""
            role_nlp = " ".join([item.lower() for item in util.split_camel_case(role)])
            result = language_model(role_nlp)
            for doc in result:
                if doc.dep_ == 'ROOT':
                    temp += util.get_plural(doc.text) + " "
                else:
                    temp += doc.text + " "
            phrase = "can have " + temp
            # phrase += util.format_role_name(role)
        return phrase

    elif role.lower() in associated_class.lower():
        if util.is_singular(cardinality):
            phrase = "has "
            phrase += util.format_concept(associated_class, language_model)
        else:
            # TODO : Handle the case where cardinality is 'many' and associated class  has  role name but it is not
            #  plural
            temp_class = ""
            ass_class = " ".join([item.lower() for item in util.split_camel_case(associated_class)])
            result = language_model(ass_class)
            for doc in result:
                if doc.dep_ == 'ROOT':
                    temp_class += util.get_plural(doc.text) + " "
                else:
                    temp_class += doc.text + " "
            phrase = "can have "
            phrase += temp_class
        return phrase

        # Case 3: auxillary verb needed along with role and class name, but role name ends with preposition
    elif ends_with_preposition(result):
        phrase = "is " + util.format_role_name(role) + " "
        if util.is_singular(cardinality):
            phrase += util.get_appropriate_article(associated_class, language_model) + " " + util.format_class_name(
                associated_class)
        else:
            ass_class = " ".join([item.lower() for item in util.split_camel_case(associated_class)])
            result = language_model(ass_class)
            for doc in result:
                if doc.dep_ == 'ROOT':
                    phrase += util.get_plural(doc.text) + " "
                else:
                    phrase += doc.text + " "
        return phrase
    else:
        # TODO check if you can use who,which etc instead of which always
        if util.is_singular(cardinality):
            phrase = "has " + util.get_appropriate_article(role, language_model)

            singular_form = util.get_singular(role)
            if isinstance(singular_form, bool):
                singular_form = role

            phrase += " " + util.get_appropriate_article(singular_form, language_model) + " " + util.format_role_name(
                singular_form)
        else:
            phrase = "can have "
            phrase += util.format_role_name(util.get_plural(role))

        phrase += " which "
        supporting_verb = ''
        if util.is_singular(cardinality):
            # Only need an article for singular class name.
            phrase += "is " + util.get_appropriate_article(associated_class, language_model) + " "
            supporting_verb = 'is'
        else:
            phrase += "are "
            supporting_verb = 'are'

        # Following code takes care of using singular/plural form of main Noun in role based on 'is/are'
        formatted_class_name = util.format_class_name(associated_class)
        formatted_class_name_list = formatted_class_name.split(" ")
        res = language_model(formatted_class_name)
        for i, token in enumerate(res):
            # To find main noun aka class name and not the adjective/adverb associated with it
            if token.dep_ == 'ROOT':
                if token.morph.get("Number") == ['Sing'] and supporting_verb == 'are':
                    plural_form = util.get_plural(token.text)
                    formatted_class_name_list[i] = plural_form
                elif token.morph.get("Number") == ['Plur'] and supporting_verb == 'is':
                    singular_form = util.get_singular(token.text)
                    formatted_class_name_list[i] = singular_form
        phrase += " ".join(formatted_class_name_list)
        return phrase


class SentenceFromAssociations(AbstractSentenceGenerator):
    def __init__(self, associations, model):
        self.associations = associations
        self.language_model = model
        # self.association_phrase = "is connected to"

        # TODO : Keep only one format either sentences list or 'relationships'  dataframe
        self.sentences = []
        self.relationships = pd.DataFrame(
            columns=['source', 'target', 'role', 'source_role', 'multiplicity', 'sentence'])
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    def get_relationships(self):
        return self.relationships

    def generate_sentences(self):
        # With role name
        for association in self.associations:
            # TODO below code generates two sentences for each association, describing each end of association in one
            #  sentence >>>>
            formatted_class1 = util.format_class_name(association['class1'])
            formatted_class2 = util.format_class_name(association['class2'])

            # Removes "Each" from start of the sentence when cardinality is too many or not there.
            # part_of_sentence = ''
            # if association['cardinality_class2'] == '':
            #     part_of_sentence += "A "
            # elif util.is_singular(association['cardinality_class2']):
            #     part_of_sentence += "Each "
            # else:
            #     part_of_sentence += "A "

            if len(association['cardinality_class2']) != 0:
                part_of_sentence = "A "
                part_of_sentence += util.format_class_name(
                    association['class1']) + " " + get_role_and_cardinality(
                    association['role_class2'],
                    association[
                        'cardinality_class2'], association['class2'], self.language_model)

                self.sentences.append(part_of_sentence)
                self.relationships.loc[len(self.relationships)] = [formatted_class1, formatted_class2,
                                                                   association['role_class2'],
                                                                   association['role_class1'],
                                                                   association[
                                                                       'cardinality_class2'],
                                                                   part_of_sentence]

            if len(association['cardinality_class1']) != 0:
                part_of_sentence = "A "
                # if association['cardinality_class1'] == '':
                #     part_of_sentence += "A "
                # elif util.is_singular(association['cardinality_class1']):
                #     part_of_sentence += "Each "
                # else:
                #     part_of_sentence += "A "
                part_of_sentence += util.format_class_name(
                    association['class2']) + " " + get_role_and_cardinality(
                    association['role_class1'], association['cardinality_class1'], association['class1'],
                    self.language_model)

                self.sentences.append(part_of_sentence)
                self.relationships.loc[len(self.relationships)] = [formatted_class2, formatted_class1,
                                                                   association['role_class1'],
                                                                   association['role_class2'],
                                                                   association[
                                                                       'cardinality_class1'],
                                                                   part_of_sentence]

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


library_associations = [
    {
        'class1': 'BookCopy',
        'class2': 'Loan',
        'cardinality_class1': '1',
        'cardinality_class2': '0..1',
        'name': '',
        'role_class1': 'borrowedBook',
        'role_class2': 'loan'
    },
    {
        'class1': 'Loan',
        'class2': 'Member',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1',
        'name': '',
        'role_class1': 'loans',
        'role_class2': 'currentHolder'
    },
    {
        'class1': 'Member',
        'class2': 'Book',
        'cardinality_class1': '0..*',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'requesters',
        'role_class2': 'booksOnHold'
    },
    {
        'class1': 'MemberCategory',
        'class2': 'LoanPeriod',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'memberCategory',
        'role_class2': 'loanPeriods'
    },
    {
        'class1': 'LoanPeriod',
        'class2': 'BookCategory',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1',
        'name': '',
        'role_class1': 'loanPeriods',
        'role_class2': 'bookCategory'
    }
]

factory_associations = [
    {
        'class1': 'Machine',
        'class2': 'Piece',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'isProducedBy',
        'role_class2': 'produces'
    },
    {
        'class1': 'Machine',
        'class2': 'Worker',
        'cardinality_class1': '*',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'operates',
        'role_class2': 'isOperatedBy'
    },
    {
        'class1': 'Factory',
        'class2': 'Worker',
        'cardinality_class1': '1',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'workplace',
        'role_class2': 'employees'
    }
]

transportation_associations = [
    {
        'class1': 'BikeStation',
        'class2': 'Bike',
        'cardinality_class1': '0..1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'parkedIn',
        'role_class2': 'bikesParked'
    },
    {
        'class1': 'SustainableCity',
        'class2': 'BikeStation',
        'cardinality_class1': '1',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'in',
        'role_class2': 'has'
    },
    {
        'class1': 'BikeStation',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'dropOffStation',
        'role_class2': 'rentals'
    },
    {
        'class1': 'BikeStation',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'pickupStation',
        'role_class2': 'rentals'
    },
    {
        'class1': 'Bike',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'rents',
        'role_class2': 'rentals'
    },
    {
        'class1': 'User',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'user',
        'role_class2': 'rentals'
    }
]

car_maintenance_associations = [
    {
        'class1': 'Service',
        'class2': 'Garage',
        'cardinality_class1': '*',
        'cardinality_class2': '1',
        'name': '',
        'role_class1': '',
        'role_class2': 'place'
    }
]

insurance_associations = [
    {
        'class1': 'Person',
        'class2': 'LifeInsuranceContract',
        'cardinality_class1': '1..*',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'beneficiaries',
        'role_class2': 'benefitsFrom'
    },
    {
        'class1': 'Car',
        'class2': 'CarInsuranceContract',
        'cardinality_class1': '1',
        'cardinality_class2': '0..1',
        'name': '',
        'role_class1': 'covers',
        'role_class2': 'coveredBy'
    }
]

production_cell_associations = [
    # {
    #     'class1': 'ProductionCell',
    #     'class2': 'Product',
    #     'cardinality_class1': '1',
    #     'cardinality_class2': '0..*',
    #     'name': '',
    #     'role_class1': '',
    #     'role_class2': 'products'
    # },
    # {
    #     'class1': 'ProductionCell',
    #     'class2': 'Unit',
    #     'cardinality_class1': '1',
    #     'cardinality_class2': '1..*',
    #     'name': '',
    #     'role_class1': '',
    #     'role_class2': 'units'
    # },
    {
        'class1': 'ProcessingUnit',
        'class2': 'TransportUnit',
        'cardinality_class1': '1',
        'cardinality_class2': '',
        'name': '',
        'role_class1': 'transportsTo',
        'role_class2': ''
    },
    {
        'class1': 'ProcessingUnit',
        'class2': 'TransportUnit',
        'cardinality_class1': '1',
        'cardinality_class2': '',
        'name': '',
        'role_class1': 'transportsFrom',
        'role_class2': ''
    }
]

flight_reservation_associations = [
    # {
    #     'class1': 'Flight',
    #     'class2': 'City',
    #     'role_class1': 'incomingFlight',
    #     'role_class2': 'flewTo',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '*'
    # },
    # {
    #     'class1': 'Flight',
    #     'class2': 'City',
    #     'role_class1': 'outgoingFlight',
    #     'role_class2': 'flewFrom',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'
    # },
    # {
    #     'class1': 'Trip',
    #     'class2': 'FlightOccurrence',
    #     'role_class1': 'partOf',
    #     'role_class2': 'flights',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1..*'
    # },
    # {
    #     'class1': 'Luggage',
    #     'class2': 'FlightOccurrence',
    #     'role_class1': 'transporting',
    #     'role_class2': 'on',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': ''
    # },
    # {
    #     'class1': 'Luggage',
    #     'class2': 'Trip',
    #     'role_class1': 'checkedLuggage',
    #     'role_class2': 'trip',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'
    # },
    # {
    #     'class1': 'FlightOccurrence',
    #     'class2': 'Plane',
    #     'role_class1': 'flies',
    #     'role_class2': 'flownBy',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'
    # },
    # {
    #     'class1': 'Seat',
    #     'class2': 'Plane',
    #     'role_class1': 'seats',
    #     'role_class2': 'installedIn',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'},
    {
        'class1': 'BookedFlight',
        'class2': 'FlightOccurrence',
        'role_class1': 'bookings',
        'role_class2': 'flight',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1'
    },
    # {
    #     'class1': 'Person',
    #     'class2': 'Trip',
    #     'role_class1': 'passenger',
    #     'role_class2': 'bookedTrips',
    #     'cardinality_class1': '1',
    #     'cardinality_class2': '0..*'
    # },
    # {
    #     'class1': 'Person',
    #     'class2': 'BookedFlight',
    #     'role_class1': 'passenger',
    #     'role_class2': 'bookedFlights',
    #     'cardinality_class1': '1',
    #     'cardinality_class2': '0..*'
    # },
    # {
    #     'class1': 'BookedFlight',
    #     'class2': 'Seat',
    #     'role_class1': 'bookedFlights',
    #     'role_class2': 'seat',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'
    # },
    # {
    #     'class1': 'FlightOccurrence',
    #     'class2': 'Flight',
    #     'role_class1': 'occurrences',
    #     'role_class2': 'flight',
    #     'cardinality_class1': '0..*',
    #     'cardinality_class2': '1'
    # }
]

hotel_reservation_associations = [
    {
        'class1': 'Room',
        'class2': 'Room',
        'role_class1': 'adjoinedRooms',
        'role_class2': 'myRoom',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1'
    },
    {
        'class1': 'Room',
        'class2': 'Booking',
        'role_class1': 'bookedRooms',
        'role_class2': 'bookings',
        'cardinality_class1': '1..*',
        'cardinality_class2': '0..*'
    },
    {
        'class1': 'Person',
        'class2': 'Booking',
        'role_class1': 'bookedBy',
        'role_class2': 'myBookings',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*'
    },
    {
        'class1': 'RoomType',
        'class2': 'Room',
        'role_class1': 'type',
        'role_class2': 'rooms',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*'
    },
    {
        'class1': 'Stay',
        'class2': 'Person',
        'role_class1': 'currentStay',
        'role_class2': 'guest',
        'cardinality_class1': '',
        'cardinality_class2': '1'
    },
    {
        'class1': 'Room',
        'class2': 'Stay',
        'role_class1': 'rooms',
        'role_class2': 'currentStay',
        'cardinality_class1': '1..*',
        'cardinality_class2': ''
    }
]

# sfa = SentenceFromAssociations(flight_reservation_associations)
# print(sfa.get_relationships())

# without role name
# for association in associations:
#     part_of_sentence = ''

#     part_of_sentence += "Each " + association['class1'] + " " + get_association_phrase(
#         association['cardinality_class2']) + " "
#     part_of_sentence += get_cardinality(association['cardinality_class2']) + " "
#     part_of_sentence += association['class2'] + " "
#     part_of_sentence += "while " + "Each " + association['class2'] + " " + 'belongs to' + " "
#     part_of_sentence += get_cardinality(association['cardinality_class1']) + " "
#     part_of_sentence += association['class1']
#     sentences.append(part_of_sentence)

# def get_role_name(role_information):
#     words = split_camel_case(role_information)
#     pos_tag = nltk.pos_tag(words)
#     if contains_verb([pair[1] for pair in pos_tag]):
#         return " ".join(words)
#     else:
#         return "has "
