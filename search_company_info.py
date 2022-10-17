import requests
import json
import csv
import sys
from prettytable import PrettyTable
import math
import time
import random


class GithubSpider:
    # Create token
    token = 'Bearer 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'
    headers_xml = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest', 'authority': 'github.com', 'Authorization': token }
    headers_common = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36',
            'Authorization': token}

    def __init__(self):
        remain = self.check_limit()
        if remain <= 0:
            print('Limit reached! Please try another github account or wait for at most 1 hour.')
            sys.exit(1)
        self.company_ls = []

    def get_data_from_url(self, url, headers):
        """获取html/json数据, 并且解码"""
        res = requests.get(url, headers=headers)
        return res.content.decode()

    def parse_data(self, json_str):
        # format: {"data":{"members":{"totalCount":4369},"repositories":{"totalCount":5124},"projects":{"totalCount":47}}}
        try:
            data = json.loads(json_str)['data']
            return {'people': data['members']['totalCount'],
                    'repositories': data['repositories']['totalCount'],
                    'projects': data['projects']['totalCount']}
        except (json.JSONDecodeError, KeyError) as e:
            return None

    def fetch_repos(self, company, nums):
        per_page = 100
        page_count = math.ceil(nums / per_page)

        keys = ['name', 'stargazers_count', 'forks_count', 'language']
        cols = ['name', 'star', 'fork', 'language']

        t = PrettyTable(cols)
        all_data = []
        for page in range(page_count):
            repo_url = 'https://api.github.com/orgs/{}/repos?per_page={}&page={}'.format(company, per_page, page + 1)

            json_str = self.get_data_from_url(repo_url, self.headers_common)
            data = json.loads(json_str)
            all_data += data
            print('Get repo count:', len(all_data), 'from url:', repo_url)

        # sort by the star count descendingly
        all_data.sort(key=lambda x: x['stargazers_count'], reverse=True)

        h_index = 0
        # show the repos as table
        for idx, row in enumerate(all_data):
            if int(row['stargazers_count']) < idx + 1:
                h_index = idx
                break
            t.add_row([row[key] for key in keys])

        print(company, 'h-index:', h_index)
        print(t)

    def display_companies(self):
        print('\nCompany sorted by the repository count desc')
        t = PrettyTable(['Company', 'Repository'])
        for row in self.company_ls:
            t.add_row(row)
        print(t)

    def check_limit(self):
        url = 'https://api.github.com/rate_limit'
        json_str = self.get_data_from_url(url, self.headers_common)
        remaining = json.loads(json_str)['resources']['core']['remaining']
        print('Github api limit for this hour is:', remaining)
        return int(remaining)

    def run(self, company):
        url = 'https://github.com/users/{}/tab_counts?repo=1&project=1&member=1'.format(company)

        json_str = self.get_data_from_url(url, self.headers_xml)
        data = self.parse_data(json_str)
        if data is None:
            print('{} not exists! Please check the company name!'.format(company))
            return

        print('\n--------------------')
        print ('People: ', data['people'])
        print ('Repositories: ', data['repositories'])
        print ('Projects: ', data['projects'])
        print('--------------------\n')

        repo_count = int(data['repositories'])

        self.fetch_repos(company, repo_count)

        self.company_ls.append([company, repo_count])
        self.company_ls.sort(key=lambda x: x[1], reverse=True)

        # show the sorted company by repo number
        self.display_companies()


if __name__ == '__main__':
    print('Fetch github organization data')
    spider = GithubSpider()
    # common company: alibaba, aws etc
    while True:
        company = input('\nInput the company name(in lower case, eg. google, microsoft, alibaba. Leave empty to exit): ')
        if not company:
            break
        spider.run(company)
