import json
from flask import Flask, request, render_template
from elasticsearch import Elasticsearch

# WEB
app = Flask(__name__)
# 全文検索DBインスタンス
es = Elasticsearch()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post', methods=['GET','POST'])
def get_request():

    value = request.args.get('text', '')
    callback = request.args.get('callback', '')

    max_score = -float('inf')
    result = ''

    for r in __reply(value):
        score = evaluate(value, r)
        if score > max_score:
            max_score = score
            result = r[1]

    dic = {'output' : [{'type' : 'text', 'value' : result }] }
    contents = callback + '(' + json.dumps(dic) + ')'
    return contents

def __reply(value):
    results = es.search(index='dialogue_pair', body={'query':{'match':{'query':value}}, 'size':100,})
    return [(result['_source']['query'], result['_source']['response'], result["_score"]) for result in results['hits']['hits']]

def evaluate(value, pair):
    #utt:     ユーザ発話
    #pair[0]: 用例ベースのtweet
    #pair[1]: 用例ベースのreply
    #pair[2]: elasticsearchのスコア
    #返り直:   評価スコア（大きいほど応答として適切)
    return pair[2]

# Main
if __name__ == "__main__":
    app.run(debug=True)
