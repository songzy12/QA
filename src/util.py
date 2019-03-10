import gensim
import io
import json
import jieba
import requests
import urllib

import pandas as pd
from matchzoo import DataPack


# model = gensim.models.Word2Vec.load('data/wiki.zh.text.jieba.model')


def es_reply(query):
    url = 'http://127.0.0.1:9200/robot_common/_search?q=question:{}'.format(
        urllib.quote(query.encode('utf8')))
    response = json.loads(requests.get(url).text)
    hits = response['hits'] if 'hits' in response else None
    if not hits or not hits['hits']:
        return []
    return [[x['_source']['question'], x['_score']] for x in hits['hits']]


def save(json_data, filename):
    with io.open(filename, 'w', encoding='utf8') as f:
        f.write(json.dumps(json_data, ensure_ascii=False, sort_keys=True, indent=4))


def prepare_data():
    text2id = {}
    
    label_file = '../data/label/match.json'
    candidate_file = '../data/label/candidate.json'

    with io.open(label_file, encoding='utf8') as f:
        m_match = json.loads(f.read())

    with io.open(candidate_file, encoding='utf8') as f:
        m_candidate = json.loads(f.read())

    relation = []
    left = []
    right = []

    num_candidate = 5
    
    for k, v in m_candidate.items():
        
        if k not in m_match or not m_match[k]:
            continue
        if k not in text2id:
            text2id[k] = 't_%d' % (len(text2id))
            left.append([text2id[k], k])
        
        for _candidate in v[:num_candidate]:
            candidate = _candidate[0]

            if candidate not in text2id:
                text2id[candidate] = 't_%d' % (len(text2id))
                right.append([text2id[candidate], candidate])
            if candidate in m_match[k]:
                relation.append([text2id[k], text2id[candidate], 1])
            else:
                relation.append([text2id[k], text2id[candidate], 0])
        
        for _candidate in v[num_candidate:]:
            candidate = _candidate[0]
            if candidate not in text2id:
                text2id[candidate] = 't_%d' % (len(text2id))
                right.append([text2id[candidate], candidate])
            if candidate in m_match[k]:
                relation.append([text2id[k], text2id[candidate], 1])

    relation = pd.DataFrame(relation, columns=['id_left', 'id_right', 'label'])
    left = pd.DataFrame(left, columns=['id_left', 'text_left'])
    left.set_index('id_left', inplace=True)
    right = pd.DataFrame(right, columns=['id_right', 'text_right'])
    right.set_index('id_right', inplace=True)

    data_pack = DataPack(relation=relation, left=left, right=right)
    dirpath = '../data'
    data_pack.save(dirpath)


if __name__ == '__main__':
    prepare_data()