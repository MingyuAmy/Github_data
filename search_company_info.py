import requests
import json
import csv
import sys
from prettytable import PrettyTable
import math
import time
import random


class GithubSpider:
    headers_xml = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest', 'authority': 'github.com' }
    headers_common = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36'}

    def __init__(self):
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
        except json.JSONDecodeError:
            print('Not found! Please check the company name!')
            sys.exit(-1)

    def is_company_exists(self, company):
        """
        Check whether the given company exists
        """
        org_url = 'https://api.github.com/orgs/{}'.format(company)
        json_str = self.get_data_from_url(org_url, self.headers_common)
        data = json.loads(json_str)
        if 'type' not in data:
            return False
        return True

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

            time.sleep(random.random())

        # sort by the star count descendingly
        all_data.sort(key=lambda x: x['stargazers_count'], reverse=True)

        # show the repos as table
        for row in all_data:
            t.add_row([row[key] for key in keys])

        print(t)

    def display_companies(self):
        print('\nCompany sorted by the repository count desc')
        t = PrettyTable(['Company', 'Repository'])
        for row in self.company_ls:
            t.add_row(row)
        print(t)

    def run(self, company):
        if not self.is_company_exists(company):
            print('{} not exists! Please check the company name!'.format(company))
            return
        url = 'https://github.com/users/{}/tab_counts?repo=1&project=1&member=1'.format(company)

        json_str = self.get_data_from_url(url, self.headers_xml)
        data = self.parse_data(json_str)

        print('\n--------------------')
        print ('People: ', data['people'])
        print ('Repositories: ', data['repositories'])
        print ('Projects: ', data['projects'])
        print('--------------------\n')

        self.fetch_repos(company, int(data['repositories']))

        self.company_ls.append([company, int(data['repositories'])])
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
