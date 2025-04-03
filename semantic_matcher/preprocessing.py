import nltk
# import stanfordnlp

# MODELS_DIR = '.'
# stanfordnlp.download('en', MODELS_DIR)  # Download the English models
# nlp = stanfordnlp.Pipeline(processors='tokenize,pos,depparse', models_dir=MODELS_DIR, treebank='en_ewt', use_gpu=True,
#                            pos_batch_size=3000)  # Build the pipeline, specify part-of-speech processor's batch size
# doc = nlp("Barack Obama was born in Hawaii.")  # Run the pipeline on input text
# doc.sentences[0].print_tokens()  # Look at the result

import stanza

nlp = stanza.Pipeline('en', processors='tokenize,pos,ner,lemma,depparse')


# doc = nlp("The simulator shall continuously monitor its connection to the SNMP manager and any linked devices.The "
#           "system operator shall display the system configuration, to which the latest warning message belongs.The "
#           "system operator shall be able to initialize the system configuration, and to edit the existing system "
#           "configuration.")

# doc = nlp("This value goes from 0 to 500 degrees")

# doc = nlp("Book's Title The simulator shall provide a function to edit the existing system configuration.")


# Find subject and object dependencies and prepositional phrases
def preprocess(sentence):
    verb_lemma = None
    verbs = []
    for token in sentence.tokens:
        if 'VB' in token.words[0].xpos:
            verb_lemma = token.words[0].lemma
            verbs.append(token.words[0].lemma)
            # print(verb_lemma)
            # break

    subject = None
    object_ = None
    transitive = False
    with_preposition = False
    relative_clauses = []

    for dep_edge in sentence.dependencies:
        if verb_lemma and dep_edge[0].lemma in verbs:
            if dep_edge[2].deprel == 'nsubj':
                subject = dep_edge[2].text
                # print("subject" , subject)
            elif dep_edge[2].deprel == 'dobj':
                object_ = dep_edge[2].text
                transitive = True
                # print("object",object)
            elif dep_edge[2].deprel.startswith('prep'):
                with_preposition = True

    for dep_edge in sentence.dependencies:
        if dep_edge[0].deprel in ['acl', 'acl:relcl']:
            relative_clause_modifier = {
                'head': dep_edge[2],
                'modifier': dep_edge[0].text,
                'relation': dep_edge[0].deprel
            }
            relative_clauses.append(relative_clause_modifier)

    # Find and extract verbal clausal complements (ccomp and xcomp)
    verbal_complements = []
    # TODO handle 'edit' case i.e. conjugate verb
    for dep_edge in sentence.dependencies:
        if dep_edge[0].deprel in ['ccomp', 'xcomp']:
            verbal_complement = {
                'head': dep_edge[2],
                'complement': dep_edge[0].text,
                'relation': dep_edge[0].deprel
            }
            verbal_complements.append(verbal_complement)

    # Find and extract non-finite verbal modifiers (vmod)
    non_finite_modifiers = []
    for dep_edge in sentence.dependencies:
        if dep_edge[0].deprel == 'advcl':
            non_finite_modifier = {
                'head': dep_edge[2],
                'modifier': dep_edge[0].text,
                'relation': dep_edge[0].deprel
            }
            non_finite_modifiers.append(non_finite_modifier)

    return transitive, with_preposition, relative_clauses, verbal_complements, non_finite_modifiers


def get_genitive_cases(sentence):
    # Aggregation : D2
    genitive_cases = []
    # TODO handle or 'Poss' in word.head.feats
    for word in sentence.words:
        # Check if the POS tag indicates a possessive form (poss) or possessive ending (case)
        if word.deprel == 'nmod:poss':
            genitive_cases.append(word.text)

    return genitive_cases


def get_aggregation(sentence):
    # Aggregation : B4
    # Define phrases indicating aggregations or compositions
    aggregation_phrases = ["contain", "is made up of", "include", "comprise", "consist of", "composed of", "made up of"]

    # Find aggregations or compositions based on depparse
    # TODO Handle multiword phrases
    aggregation_sentences = []
    # for sent in doc.sentences:

    for length in range(1, 4):  # Adjust the range based on the maximum length of your aggregation phrases
        for i in range(len(sentence.words) - length + 1):
            phrase_candidate = ' '.join([sentence.words[i + j].lemma for j in range(length)])
            if phrase_candidate in aggregation_phrases and sentence.words[i].deprel == 'root':
                # Find the subject of the aggregation phrase
                subject = [w.text for w in sentence.words if w.head == sentence.words[i].id and w.deprel == 'nsubj']
                aggregation_sentences.append((subject, phrase_candidate, [w.text for w in sentence.words]))

    # Print the result
    # for subject, aggregation_phrase, objects in aggregation_sentences:
    #     print(f"Subject: {subject}, Aggregation Phrase: {aggregation_phrase}, Objects: {objects}")

    return aggregation_sentences


def get_generalizations(sentence):
    # Generalization D3
    # Find adjectival modifications of NPs based on depparse
    adjectival_modifications = []
    # for sent in doc.sentences:

    for word in sentence.words:
        if word.deprel == 'amod' and sentence.words[word.head - 1].deprel == 'nsubj':
            # adjectival modification where amod is attached to nsubj
            adjective = word.text
            noun = sentence.words[word.head - 1].text
            adjectival_modifications.append((adjective, noun))

    # Print the result
    # for adjective, noun in adjectival_modifications:
    #     print(f"Adjective: {adjective}, Noun: {noun}")

    # Generalization B5
    # Define phrases indicating relationships
    relationship_phrases = ["is a", "type of", "kind of", "may be", "example of"]

    # Find relationships based on depparse
    # TODO Handle multi word
    relationship_sentences = []
    # for sent in doc.sentences:
    for i, word in enumerate(sentence.words):
        complete_word = word.lemma
        if i < len(sentence.words) - 1:
            complete_word += " " + sentence.words[i + 1].lemma
        # if complete_word in relationship_phrases and word.deprel == 'cop':
        if complete_word in relationship_phrases:
            # Find the subject and complement of the relationship
            subject = [w.text for w in sentence.words if w.head == word.head and w.deprel == 'nsubj']
            complement = [w.text for w in sentence.words if w.head == word.head and w.deprel == 'attr']
            relationship_sentences.append((subject, word.lemma, complement))

    # Print the result
    # for subject, relationship, complement in relationship_sentences:
    #     print(f"Subject: {subject}, Relationship: {relationship}, Complement: {complement}")

    return adjectival_modifications, relationship_sentences


def get_attributes(sentence):
    # Extract information based on specified patterns
    identified_by_info = []
    recognized_by_info = []
    has_info = []
    adjective_info = []
    intransitive_verb_info = []

    for word in sentence.words:
        # Extract information for "identified by" and "recognized by"
        # D1
        if word.lemma == 'identify' and word.deprel == 'acl:relcl':
            identified_by_info.append((word.head, 'identified by', word.text))
        elif word.lemma == 'recognize' and word.deprel == 'acl:relcl':
            recognized_by_info.append((word.head, 'recognized by', word.text))

        # Extract information for "has"
        if word.lemma == 'have' and word.deprel == 'aux' and sentence.words[word.head - 1].lemma == 'have':
            has_info.append((word.head.head.text, 'has', word.head.text))

        if word.lemma == 'have' and word.deprel == 'root':
            for dependency in sentence.dependencies:
                if dependency[0].lemma == word.lemma:
                    if dependency[2].deprel == 'nsubj':
                        subject = dependency[2].text
                        has_info.append(('has', subject))
                    elif dependency[2].deprel == 'obj' or dependency[2].deprel == 'dobj':
                        object = dependency[2].text
                        has_info.append(('has', object))

        # D2
        # Extract information for adjectives of adjectivally modified NP
        if word.deprel == 'amod' and sentence.words[word.head - 1].deprel == 'nsubj':
            adjective_info.append((sentence.words[word.head - 1].text, 'has attribute', word.text))

        # D4
        # Extract information for intransitive verbs with an adverb
        if word.deprel == 'advmod' and sentence.words[word.head - 1].deprel == 'root' and sentence.words[
            word.head - 1].upos == 'VERB':
            intransitive_verb_info.append((sentence.words[word.head - 1].text, 'has attribute', word.text))

    # Print the result
    # print("Identified By Information:", identified_by_info)
    # print("Recognized By Information:", recognized_by_info)
    # print("Has Information:", has_info)
    # print("Adjective Information:", adjective_info)
    # print("Intransitive Verb Information:", intransitive_verb_info)

    attributes = identified_by_info + recognized_by_info + has_info + adjective_info + intransitive_verb_info
    return attributes


bank = ("A banking system allows its customers to manage their funds using bank accounts. Customers can open accounts "
        "with the bank, and subsequently deposit money into their accounts. At any time, the owner of a bank account "
        "can check the current balance.")

smart_city = ("A smart city is able to report the quality of the air in each of its neighborhoods. Both cities and "
              "neighborhoods have unique names. In each neighborhood, there are several sensors to measure different "
              "pollutants which are CO, O3, SO2, NO2 and others. The measurements of those sensors are aggregated and "
              "the Air Quality Index (AQI) is calculated. This value goes from 0 to 500 degrees. This resulting index "
              "is displayed in a display located in the center of the neighborhood. For each display, its size and "
              "resolution are known")

production_cell = ("A production cell is an automated cyber-physical manufacturing system for products. It is "
                   "typically composed of a set of processing units and transport units that transport the item that "
                   "is being manufactured from one processing unit to the next. Examples of processing units are "
                   "presses and cutting lasers. Examples of transport units include conveyor belts and robot arms.")

banking_system = ("We need to model a banking system, which is a software application that manages financial "
                  "transactions for a financial institution. It manages customer account information; communicates "
                  "with various channels, such as ATMs; and processes transactions that can be either a withdrawal, "
                  "a deposit, or a transfer. A bank can have different types of accounts. The system must maintain "
                  "accurate and up-to-date information about each customer. Finally, the banking system also manages "
                  "employee information.")

hotel_system = ("We need to model a hotel system that is going to be used by hotels to manage their operations and "
                "provide services to their guests. The system should be able to handle various types of room "
                "reservations, such as single room, double room, suite, and so on. It should also be able to handle "
                "guest check-ins and check-outs. This involves collecting guest information, assigning rooms, "
                "and processing payments. Restaurant management is another important aspect of the hotel domain. It "
                "involves managing restaurant reservations, tracking table availability, and processing food and "
                "beverage orders. Additionally, the software should be able to schedule housekeeping tasks, "
                "track the status of cleaning and maintenance tasks, and manage housekeeping staff assignments. "
                "Finally, this system should be able to handle various types of staff tasks.")

library_management_system = ("We need to model a library system that is going to be used to manage various operations "
                             "and provide library services to library users. It maintains accurate and up-to-date "
                             "information about each item in the library collection. Library materials, "
                             "including books, magazines, DVDs, and other media should be stored and managed by the "
                             "software. The system must be able to track the library items, including checkouts, "
                             "renewals, and returns. The system should be capable of scheduling appointments for "
                             "users, managing the availability of library staff and resources. It also manages "
                             "library billing and membership information.")

online_shopping_system = ("We need to model an online shopping system for a software application that is going to be "
                          "used to manage various operations and provide e-commerce services to customers. Product "
                          "catalogs, including descriptions, images, pricing, and availability should be stored and "
                          "managed by the software. The system must be able to process online orders, "
                          "including tracking shipments, managing returns, and processing payments securely. The "
                          "system should be capable of scheduling deliveries for orders, managing the availability of "
                          "products and resources, and providing customer support services.")

factory_system = ("A factory is composed of a number of machines that produce pieces. Each factory is located in a "
                  "city. For each machine, we know its speed and capacity. For each piece, we need to store its "
                  "width, height and depth. There are workers working at the factory. Each machine is operated by one "
                  "or more workers and, for each worker, we need to store their id, name and salary.")

transportation_system = (
    "Cities put in place bike rental systems to encourage their citizens to be more sustainable. For each city, "
    "we need to store its name and country. Cities have bike stations located at different addresses. Apart from the "
    "address, for each bike station we need to store its name and the number of spots that it has to park bikes. When "
    "bikes are not in use, they are parked in bike stations. For each bike, we store its code as an integer and the "
    "price per hour. Note that different bikes might have different prices per hour."
    "Bikes are rented by users. For each user we need to keep their id, name and credit card information. For each "
    "rental, we need to keep track of the start and end date, the pickup station, the dropoff "
    "station, the user who has rented the bike and the bike that has been rented.")

doc = nlp(smart_city)

necessary_sentences = []
unnecessary_sentences = []

for sentence in doc.sentences:
    # sentence.print_tokens()
    transitive, with_preposition, relative_clauses, verbal_complements, non_finite_modifiers = preprocess(sentence)
    genitive_cases = get_genitive_cases(sentence)
    aggregation_sentences = get_aggregation(sentence)
    adjectival_modifications, relationship_sentences = get_generalizations(sentence)
    attributes = get_attributes(sentence)

    # print(transitive)
    # print(with_preposition)
    # print(relative_clauses)
    # print(verbal_complements)
    # print(non_finite_modifiers)
    # print(genitive_cases)
    # print(aggregation_sentences)
    # print(adjectival_modifications)
    # print(relationship_sentences)
    # print(attributes)

    if transitive or with_preposition or len(relative_clauses) > 0 or len(verbal_complements) > 0 or len(
            non_finite_modifiers) > 0 or len(genitive_cases) > 0 or len(aggregation_sentences) > 0 or len(
        adjectival_modifications) > 0 or len(relationship_sentences) > 0 or len(attributes) > 0:
        necessary_sentences.append(sentence)
    else:
        unnecessary_sentences.append(sentence)

for sentence in unnecessary_sentences:
    words = [word.text for word in sentence.words]
    print(words)
