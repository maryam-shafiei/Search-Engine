from __future__ import unicode_literals
import math
import matplotlib.pyplot as plt
from parsivar import *
from hazm import stopwords_list
import json
import re

normalizer = Normalizer()
tokenizer = Tokenizer()
stemmer = FindStems()

stop_words = set(stopwords_list())
puncs = {'(', ')', '/', '،', '.', '«', '»', '؟', ':'}
tokens = []

dictionary = {}


def preproccesing(content):
    docToken = []
    normalized_content = normalizer.normalize(content)
    word_token = tokenizer.tokenize_words(normalized_content)
    for i in range(len(word_token)):
        if word_token[i] not in stop_words and word_token[i] not in puncs:
            docToken.append(stemmer.convert_to_stem(word_token[i]))

    tokens.append(docToken)


def make_positional_index(terms):
    for i in range(len(terms)):
        for j in range(len(terms[i])):
            if terms[i][j] in dictionary:
                dictionary[terms[i][j]]["total_repeat"] += 1
                if i in dictionary[terms[i][j]]:
                    dictionary[terms[i][j]][i]["number"] += 1
                    dictionary[terms[i][j]][i]["list"].append(j)
                else:
                    dictionary[terms[i][j]][i] = {
                        "number": 1,
                        "list": [j]
                    }
            else:
                dictionary[terms[i][j]] = {
                    "total_repeat": 1,
                    i: {
                        "number": 1,
                        "list": [j]
                    }
                }


def word_answer(dict, wrd):
    docsId = {}
    if wrd in dict.keys():
        docsId = dict[wrd]

    print(docsId)
    return docsId


def multi_word_answer(dict, query):
    query_wrd = []
    normalized_query = normalizer.normalize(query)
    word_token_query = tokenizer.tokenize_words(normalized_query)
    for i in range(len(word_token_query)):
        if word_token_query[i] not in stop_words and word_token_query[i] not in puncs:
            query_wrd.append(stemmer.convert_to_stem(word_token_query[i]))

    ans = []
    for w in query_wrd:
        ans.append(word_answer(dict, w))
    print(ans)
    return ans


def quot_answer(dict, phrase):
    phrase_words = phrase.split(" ")
    docID_ans = set()
    intersect = set()
    ans_list = []
    for i in range(len(phrase_words) - 1):
        if i > 0:
            x_wrd = y_wrd
            x = y
        else:
            x_wrd = phrase_words[i]
            x = word_answer(dict, x_wrd)
        y_wrd = phrase_words[i + 1]
        y = word_answer(dict, y_wrd)
        if len(docID_ans) == 0:
            for x_k in x.keys():
                if x_k != 'total_repeat' and x_k in y.keys():
                    intersect.add(x_k)
        else:
            for x_k in x.keys():
                if x_k != 'total_repeat' and x_k in y.keys() and x_k in docID_ans:
                    intersect.add(x_k)

        if len(intersect) != 0:
            print(intersect)
            for j in intersect:
                x_pos = x[j]["list"]
                y_pos = y[j]["list"]
                for k in x_pos:
                    for r in y_pos:
                        if r - k == 1:
                            docID_ans.add(j)
                            ans_list.append({j: x[j]})
                            ans_list.append({j: y[j]})
        else:
            break
    print(docID_ans)
    print(ans_list)
    return ans_list


def not_ans(dict, not_wrd, other_words, is_not_wrd_phrase):
    if is_not_wrd_phrase == 0:
        not_wrd_doc = word_answer(dict, not_wrd)
    else:
        not_wrd_doc = quot_answer(dict, not_wrd)
    for x in other_words:
        for y, y_val in list(x.items()):
            if is_not_wrd_phrase == 0:
                if y != 'total_report' and y in not_wrd_doc:
                    del x[y]
            else:
                if y != 'total_report':
                    for s in not_wrd_doc:
                        if y in s:
                            del x[y]

    return other_words


def ranking_results(res):
    id_num = {}
    for i in res:
        for j, v in i.items():
            if j != 'total_repeat':
                if j in id_num:
                    id_num[j] += v['number']
                else:
                    id_num[j] = v['number']
    sorted_id_num = dict(sorted(id_num.items(), key=lambda x: x[1], reverse=True))
    print(sorted_id_num)
    return sorted_id_num


def show_res(dict_res, data):
    for r in dict_res:
        print(data[str(r)]['title'] + ": ")
        print(data[str(r)]['url'])
        print()


def eval_heaps(data, n, f):
    vocab = set()
    stem_token = set()
    non_stem_token = set()
    if f == 0:
        for i in range(n):
            content = data[str(i)]['content']
            vocab.update(tokenizer.tokenize_words(content))
            normalized_content = normalizer.normalize(content)
            word_token = tokenizer.tokenize_words(normalized_content)
            for i in range(len(word_token)):
                if word_token[i] not in stop_words and word_token[i] not in puncs:
                    non_stem_token.add(word_token[i])
                    stem_token.add(stemmer.convert_to_stem(word_token[i]))
    else:
        for i in data:
            content = data[str(i)]['content']
            vocab.update(tokenizer.tokenize_words(content))
            normalized_content = normalizer.normalize(content)
            word_token = tokenizer.tokenize_words(normalized_content)
            for i in range(len(word_token)):
                if word_token[i] not in stop_words and word_token[i] not in puncs:
                    non_stem_token.add(word_token[i])
                    stem_token.add(stemmer.convert_to_stem(word_token[i]))
    return len(non_stem_token), len(stem_token), len(vocab)


def eval_zipf(data):
    vocab = []
    vocab_freq = {}
    before_stop = set()
    after_stop = set()
    for i in data:
        content = data[str(i)]['content']
        vocab.extend(tokenizer.tokenize_words(content))
        normalized_content = normalizer.normalize(content)
        word_token = tokenizer.tokenize_words(normalized_content)
        for i in range(len(word_token)):
            before_stop.add(stemmer.convert_to_stem(word_token[i]))
            if word_token[i] not in stop_words and word_token[i] not in puncs:
                after_stop.add(stemmer.convert_to_stem(word_token[i]))
    for item in vocab:
        if item in vocab_freq:
            vocab_freq[item] += 1
        else:
            vocab_freq[item] = 1
    vocab_freq = dict(sorted(vocab_freq.items(), key=lambda x: x[1], reverse=True))
    return vocab_freq, before_stop, after_stop


f = open('IR_data_news_12k.json', 'r', encoding='utf-8')
data = json.load(f)
# fw = open("readme.txt", 'a', encoding='utf-8')

# x_b = []
# x_a = []
# y_b = []
# y_a = []
# dict_freq, b_, a_ = eval_zipf(data)
# count = 0
# for i in dict_freq:
#     count += 1
#     if i in b_:
#         x_b.append(math.log10(count))
#         y_b.append(math.log10(dict_freq[i]))
#     if i in a_:
#         x_a.append(math.log10(count))
#         y_a.append(math.log10(dict_freq[i]))

# xx = [0, 1, 2, 3, 4, 5]
# yy = [5, 4, 3, 2, 1, 0]
# fig = plt.figure()
# fig.add_subplot(1, 2, 1)
# plt.title("Before")
# plt.plot(x_b, y_b)
# plt.plot(xx, yy)
# fig.add_subplot(1, 2, 2)
# plt.title("After")
# plt.plot(x_a, y_a)
# plt.plot(xx, yy)
# plt.show()



for i in data:
    preproccesing(data[i]["content"].replace("انتهای پیام", ""))

make_positional_index(tokens)
while 1:
    query = input('please enter your query: ')
    quots = re.findall('"([^"]*)"', query)
    nots = []
    edit_query = query
    words = query.split(" ")
    for i in range(len(words)):
        if words[i] == '!':
            nots.append(words[i + 1])
    for i in nots:
        edit_query = query.replace(i, "")
    for i in quots:
        edit_query = edit_query.replace(i, "")

    edit_query = edit_query.replace('"', "")
    edit_query = edit_query.replace('!', "")

    a = multi_word_answer(dictionary, edit_query)
    for i in quots:
        a.extend(quot_answer(dictionary, i))

    c = []
    flag = 0
    for i in nots:
        flag = 1
        if len(c) == 0:
            c = not_ans(dictionary, i, a, 0)
        else:
            c = not_ans(dictionary, i, c, 0)

    if flag == 0:
        c = a
    show_res(ranking_results(c), data)

    print(nots)
    print(quots)
    print(edit_query)


# print("500:")
# print(eval_heaps(data, 500, 0))
# print("1000:")
# print(eval_heaps(data, 1000, 0))
# print("1500:")
# print(eval_heaps(data, 1500, 0))
# print("2000:")
# print(eval_heaps(data, 2000, 0))
# nsteam500, steam500, vocab500 = eval_heaps(data, 500, 0)
# nsteam1000, steam1000, vocab1000 = eval_heaps(data, 1000, 0)
# nsteam1500, steam1500, vocab1500 = eval_heaps(data, 1500, 0)
# nsteam2000, steam2000, vocab2000 = eval_heaps(data, 2000, 0)

# print("total:")
# print(eval_heaps(data, 2000, 1))

# vocab_x = [math.log10(vocab500), math.log10(vocab1000), math.log10(vocab1500), math.log10(vocab2000)]
# nsteam_y = [math.log10(nsteam500), math.log10(nsteam1000), math.log10(nsteam1500), math.log10(nsteam2000)]
# steam_y = [math.log10(steam500), math.log10(steam1000), math.log10(steam1500), math.log10(steam2000)]
# plt.plot(vocab_x, nsteam_y)
# plt.plot(vocab_x, steam_y)

# plt.show()
