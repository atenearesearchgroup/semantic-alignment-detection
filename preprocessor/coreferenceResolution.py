import pandas as pd
import stanza

text = "John is a programmer. He loves his job. He is good at it."

# text = ("A production cell is an automated cyber-physical manufacturing system for products. It is typically
# composed " "of a set of processing units and transport units that transport the item that is being manufactured
# from one " "processing unit to the next. Examples of processing units are presses and cutting lasers. Examples of "
# "transport units include conveyor belts and robot arms")

# Start CoreNLP client
stanza.download("en")  # Download English models
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,ner,depparse,coref")


def get_preprocessed_text(text):
    text = text.replace("e.g.", "").replace("i.e.", "").replace("etc.", "")
    doc = nlp(text)

    original_sentences = []
    for sent_idx, sent in enumerate(doc.sentences):
        original_sentences.append(sent.text)

    replacement_words = []

    # Extract coreference clusters
    for cluster in doc.coref:
        main_mention = cluster.mentions[cluster.representative_index]
        main_mention_text = " ".join(
            [doc.sentences[main_mention.sentence].words[i].text for i in
             range(main_mention.start_word, main_mention.end_word)]
        )

        for mention in cluster.mentions:
            if mention.sentence != main_mention.sentence:
                replacement_words.append((mention.sentence, mention.start_word, mention.end_word, main_mention_text))

    # Reconstruct sentences with resolved coreferences
    new_sentences = []
    for sent_idx, sent in enumerate(doc.sentences):
        words = [word.text for word in sent.words]
        for mention_sentence, start, end, replacement in replacement_words:
            if mention_sentence == sent_idx:
                words[start:end] = [replacement]
        new_sentences.append(" ".join(words))

    return original_sentences, new_sentences


# preprocessed_text = get_preprocessed_text(text)
# print(preprocessed_text)
