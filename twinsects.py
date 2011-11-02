#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# @author:     starenka
# @email:      'moc]tod[liamg].T.E[0aknerats'[::-1]
import itertools, string
from collections import defaultdict

from flask import Flask, render_template, request
from werkzeug.contrib.cache import SimpleCache

import simplejson
import tweepy

app = Flask(__name__)
app.config.from_object('settings')
cache = SimpleCache()

@app.context_processor
def base_context():
    return dict(settings=app.config, )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title=u"404"), 404


@app.route('/faq')
def faq():
    return render_template('faq.html', title=u"FAQ")


@app.route('/')
def index():
    accounts = request.args.get('accounts','')
    accounts = accounts.split()[:app.config['MAX_ACCOUNTS']] if accounts else app.config['DEFAULT_ACCOUNTS']
    data = {}
    venn = False
    if accounts:
        data, canvas = _go(accounts)
        if len(accounts) in range(2, 5):
            venn = True

        return render_template('generator.html', title=u"NOM NOM NOM",
                               data=data, canvas=canvas,
                               accounts=accounts, venn=venn,
                               venn_groups=len(accounts)
        )


def _get_followers(accounts):
    data = defaultdict(set)
    for account in accounts:
        cached = cache.get(account)
        if cached is None:
            try:
                data[account] = set(tweepy.API().followers_ids(account)[0])
                cache.set(account, data[account], timeout=app.config['CACHE_MINUTES'] * 60)
            except tweepy.error.TweepError:
                pass
        else:
            data[account] = cached
    return data


def _venn(data, r=0):
    r = r if r else len(data.keys())
    for v in itertools.combinations(data.keys(), r):
        vsets = [data[x] for x in v]
        yield tuple(sorted(v)), reduce(lambda x, y: x.intersection(y), vsets),


def _go(accounts):
    data = _get_followers(accounts)
    ret = {'combs': [], 'accounts': data}
    canvas = {'data': {}, 'legend': {}}
    map = defaultdict(str)
    for (account, followers), letter in zip(data.items(), list(string.uppercase[:len(data)])):
        canvas['data'][letter] = len(followers)
        canvas['legend'][letter] = account
        map[account] = letter
    for r in range(2, len(data.keys()) + 1):
        for accounts, common in _venn(data, r):
            maccs = ''.join(sorted([map[account] for account in accounts]))
            uniq = len(set(itertools.chain.from_iterable([(data[acc]) for acc in accounts])))
            canvas['data'][maccs] = len(common)
            one = {'accounts': ' '.join(accounts),
                   'uniq': uniq,
                   'common': common,
                   'common_count': len(common),
                   'ratio': float(len(common)) / uniq * 100
            }
            ret['combs'].append(one)

    return ret, simplejson.dumps(canvas)

if __name__ == '__main__':
    app.run()