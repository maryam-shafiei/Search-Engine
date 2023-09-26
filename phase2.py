from __future__ import unicode_literals
import math
from parsivar import *
from hazm import stopwords_list
import json

normalizer = Normalizer()
tokenizer = Tokenizer()
stemmer = FindStems()

stop_words = set(stopwords_list())
puncs = {'(', ')', '/', '،', '.', '«', '»', '؟', ':'}
tokens = []

weight_doc_vectors = []

dictionary = {}
champion_dictionary = {}


def preproccesing(content, token_arr):
    docToken = []
    normalized_content = normalizer.normalize(content)
    for c in puncs:
        content = content.replace(c, "")
    word_token = tokenizer.tokenize_words(normalized_content)
    for i in range(len(word_token)):
        if word_token[i] not in stop_words and word_token[i] not in puncs:
            docToken.append(stemmer.convert_to_stem(word_token[i]))

    token_arr.append(docToken)


def term_frequency(term, docID, dict):
    return math.log10(dict[term][docID]['number']) + 1


def document_frequency(term):
    if term in dictionary:
        return len(dictionary[term]) - 1
    else:
        return 0


def idf(term, doc_collection_size):
    if term in dictionary:
        return math.log10(doc_collection_size/document_frequency(term))
    else:
        return 0


def calc_weight(doc_collection_size, dict):
    for x in dict.keys():
        for y in dict[x]:
            if y != 'total_repeat':
                dict[x][y]["weight"] = term_frequency(x, y, dict) * idf(x, doc_collection_size)


def make_positional_index(terms, dict):
    for i in range(len(terms)):
        for j in range(len(terms[i])):
            if terms[i][j] in dict:
                dict[terms[i][j]]["total_repeat"] += 1
                if i in dict[terms[i][j]]:
                    dict[terms[i][j]][i]["number"] += 1
                    dict[terms[i][j]][i]["list"].append(j)
                else:
                    dict[terms[i][j]][i] = {
                        "number": 1,
                        "list": [j]
                    }
            else:
                dict[terms[i][j]] = {
                    "total_repeat": 1,
                    i: {
                        "number": 1,
                        "list": [j],
                        "weight": 0
                    }
                }


def make_champion_list(dict):
    for term in dict:
        term_docs = {}
        for doc in dict[term]:
            if doc != 'total_repeat':
                term_docs[doc] = dict[term][doc]
        champion_dictionary[term] = {i: j for i, j in sorted(term_docs.items(), key=lambda x: x[1]['weight'], reverse=True)[:1000]}


def search(dict, len_2, q_dict, score):
    for x in dict:
        for dID in dict[x]:
            if dID != 'total_repeat':
                len_2[dID] += pow(dict[x][dID]['weight'], 2)

    for q_term in q_dict.keys():
        if q_term in dict:
            for word_doc in dict[q_term]:
                if word_doc != 'total_repeat':
                    score[word_doc] += q_dict[q_term][0]["weight"] * dict[q_term][word_doc]["weight"]


def show_res(dict_res, data):
    for r in dict_res:
        print(data[str(r)]['title'] + ": ")
        print(data[str(r)]['url'])
        print()


f = open('IR_data_news_12k.json', 'r', encoding='utf-8')
data = json.load(f)

document_collection_size = 0
for i in data:
    preproccesing(data[i]["content"].replace("انتهای پیام", ""), tokens)
    document_collection_size += 1

make_positional_index(tokens, dictionary)
calc_weight(document_collection_size, dictionary)
make_champion_list(dictionary)
while True:
    query = input('please enter your query: ')
    q_tokens = []
    q_dictionary = {}
    preproccesing(query, q_tokens)
    make_positional_index(q_tokens, q_dictionary)
    calc_weight(document_collection_size, q_dictionary)
    print(q_dictionary)

    scores = [0] * document_collection_size
    length_2 = [0] * document_collection_size
    q_length_2 = 0

    for x in q_dictionary:
        q_length_2 += pow(q_dictionary[x][0]['weight'], 2)

    champ_off_on = int(input('Use champion list? 1)YES 2)NO '))
    if champ_off_on == 2:
        search(dictionary, length_2, q_dictionary, scores)

    elif champ_off_on == 1:
        search(champion_dictionary, length_2, q_dictionary, scores)

    if q_length_2 != 0:
        for i in range(document_collection_size):
            if length_2[i] != 0:
                scores[i] /= math.sqrt(length_2[i]*q_length_2)

        res = sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)[:10]

        if champ_off_on == 1 and len(res) < 10:
            search(dictionary, length_2, q_dictionary, scores)
            for i in range(document_collection_size):
                if length_2[i] != 0:
                    scores[i] /= math.sqrt(length_2[i] * q_length_2)
            res = sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)[:10]
    else:
        res = []
    print(res)
    show_res(res, data)