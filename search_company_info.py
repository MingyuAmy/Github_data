import requests
import json
import csv
import sys


class GithubSpider:
    def __init__(self, company):
        if not self.is_company_exists(company):
            print('{} not exists! Please check the company name!'.format(company))
            sys.exit(-1)
        self.url = 'https://github.com/users/{}/tab_counts?repo=1&project=1&member=1'.format(company)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest', 'authority': 'github.com' }

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
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36'}
        json_str = self.get_data_from_url(org_url, headers)
        data = json.loads(json_str)
        if 'type' not in data:
            return False
        return True


    def run(self):
        json_str = self.get_data_from_url(self.url, self.headers)
        data = self.parse_data(json_str)

        print('\n--------------------')
        print ('People: ', data['people'])
        print ('Repositories: ', data['repositories'])
        print ('Projects: ', data['projects'])
        print('--------------------\n')


if __name__ == '__main__':
    print('Fetch github organization data')
    # common company: alibaba, aws etc
    while True:
        company = input('Input the company name(in lower case, eg. google, microsoft, alibaba. Leave empty to exit): ')
        if not company:
            break
        spider = GithubSpider(company)
        spider.run()

