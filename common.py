#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# provide common util methods for the scripts

import requests
import json
import math
import hashlib
import os.path
import csv
from datetime import datetime

# Create token from github account, settings > developer settings > Personal access tokens
_token = 'Bearer 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'
_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36',
        'Authorization': _token}

_API = {
    'api_limit': 'https://api.github.com/rate_limit',
    'fetch_repo': 'https://api.github.com/orgs/{}/repos?per_page={}&page={}',
    'company_info': 'https://api.github.com/orgs/{}',
    'repo_contributor': 'https://api.github.com/repos/{}/{}/contributors?per_page={}'
}

# cache util methods
# ---------------------
def read_cache(cache_fullpath):
    with open(cache_fullpath, 'r') as fd:
        json_str = fd.read()
    return json_str

def write_cache(cache_fullpath, json_str):
    with open(cache_fullpath, 'w') as fd:
        fd.write(json_str)

def cache_path(key, filename=None):
    key = hashlib.md5(key.encode()).hexdigest()
    cache_fname = key + '.json' if filename is None else filename
    cache_fullpath = os.path.join('cache', cache_fname)
    return cache_fullpath

def create_cache_dir(filename='cache'):
    if not os.path.exists(filename):
        os.mkdir(filename)
# ---------------------

def get_data_from_url(url, use_cache=False):
    """获取html/json数据, 并且解码"""
    cache_fullpath = cache_path(url)
    if use_cache and os.path.exists(cache_fullpath):
        json_str = read_cache(cache_fullpath)
    else:
        res = requests.get(url, headers=_headers)
        json_str = res.content.decode()
        if use_cache:
            write_cache(cache_fullpath, json_str)
    return json_str


def get_api_limit():
    json_str = get_data_from_url(_API['api_limit'], False)
    try:
        remaining = json.loads(json_str)['resources']['core']['remaining']
        print('Github api limit for this hour is:', remaining)
        return int(remaining)
    except (json.JSONDecodeError, KeyError) as e:
        print('Illegal token')
        return 0

def get_company_repos(company, repo_num):
    cache_fullpath = cache_path('repos-{}'.format(company))
    if os.path.exists(cache_fullpath):
        json_str = read_cache(cache_fullpath)
        return json.loads(json_str)

    per_page = 100
    page_count = math.ceil(repo_num / per_page)

    result = []
    for page in range(page_count):
        repo_url = _API['fetch_repo'].format(company, per_page, page + 1)
        json_str = get_data_from_url(repo_url)
        data = json.loads(json_str)
        result += data
        print('Get repo count:', len(result), 'from url:', repo_url)
    write_cache(cache_fullpath, json.dumps(result))
    return result

# cache in high level, so skip cache this one
def get_repo_contributors(url):
    per_page = 100
    result = []
    page_no = 1
    while True:
        repo_url = url + '?per_page=100&page=' + str(page_no)
        json_str = get_data_from_url(repo_url)
        try:
            data = json.loads(json_str)
            result += data
        except (json.JSONDecodeError, KeyError) as e:
            print('Failed to get contributors from url:', repo_url)
            break
        print('Get contributors:', len(result), 'from url:', repo_url)
        if len(data) < 100:
            break
        page_no += 1

    return result

def parse_company_status(json_str):
    try:
        data = json.loads(json_str)
        return {'followers': data['followers'],
                'repositories': data['public_repos'],
                'name': data['name'],
                'description': data['description'],
                'created_at': data['created_at'][:10]
               }
    except (json.JSONDecodeError, KeyError) as e:
        return None

def get_company_status(company):
    url = _API['company_info'].format(company)
    json_str = get_data_from_url(url)
    data = parse_company_status(json_str)
    if data is None:
        print('{} not exists! Please check the company name!'.format(company))
    return data


def fetch_contributors_for_repos(repos):
    # also needs to do with pagination
    # e.g. https://api.github.com/repos/google/guava/contributors?per_page=100
    contributors = set()
    for repo in repos:
        items = get_repo_contributors(repo['contributors_url'])
        for item in items:
            if type(item) == dict and 'login' in item:
                contributors.add(item['login'])
            else:
                print('[error] Found illegal contributor:', item)
    print('Find', len(contributors), 'contributors')
    return contributors


def fetch_contributors_for_company(company):
    cache_fullpath = cache_path('contributors-{}'.format(company))
    if os.path.exists(cache_fullpath):
        json_str = read_cache(cache_fullpath)
        return set(json.loads(json_str))

    data = get_company_status(company)
    repo_count = int(data['repositories'])
    repos = get_company_repos(company, repo_count)
    result = fetch_contributors_for_repos(repos)

    write_cache(cache_fullpath, json.dumps(list(result)))
    return result


def get_common_contributors(company_1, company_2):
    contr1 = fetch_contributors_for_company(company_1)
    contr2 = fetch_contributors_for_company(company_2)
    # find the common one
    return contr1.intersection(contr2)

def get_time_str(timeObj, timeFormat='%y-%m-%d_%H_%M'):
    return datetime.strftime(timeObj, timeFormat)

def save_to_csv(filename, header, rows):
    """
    Save data to csv file
    """
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        # first write header and use comma separated
        writer.writerow(header)
        # write data to csv file
        for row in rows:
            writer.writerow(row)
