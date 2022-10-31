#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import json
import sys
from prettytable import PrettyTable
from common import  get_api_limit, get_company_repos, get_company_status, fetch_contributors_for_company, create_cache_dir

class GithubSpider:

    def __init__(self):
        remain = get_api_limit()
        if remain <= 0:
            print('Limit reached! Please try another github account or wait for at most 1 hour.')
            sys.exit(1)
        self.company_ls = []


    def fetch_repos(self, company, nums):
        keys = ['name', 'stargazers_count', 'forks_count', 'language']
        cols = ['name', 'star', 'fork', 'language']

        repos = get_company_repos(company, nums)

        t = PrettyTable(cols)
        # sort by the star count descendingly
        repos.sort(key=lambda x: x['stargazers_count'], reverse=True)

        h_index = 0
        # show the repos as table
        for idx, row in enumerate(repos):
            if int(row['stargazers_count']) < idx + 1:
                h_index = idx
                break
            t.add_row([row[key] for key in keys])

        print(company, 'h-index:', h_index)
        print(t)
        return repos

    def display_companies(self):
        print('\nCompany sorted by the repository count desc')
        t = PrettyTable(['Company', 'Repository', 'Contributor'])
        for row in self.company_ls:
            t.add_row(row[0:2] + [len(row[2])])
        print(t)

    def display_contributor_matrix(self):
        if len(self.company_ls) <= 1:
            return
        print('\nContribution matrix:')
        n = len(self.company_ls)
        t = PrettyTable(['\\'] + [row[0] for row in self.company_ls])

        # calculate the intersect of common contributors between two company
        for one in self.company_ls:
            common = one[0:1]
            for other in self.company_ls:
                common.append(len(one[2].intersection(other[2])))
            t.add_row(common)
        print(t)


    def run(self, company):
        data = get_company_status(company)
        if not data:
            return

        print('\n--------------------')
        print ('Name: ', data['name'])
        print ('Repositories: ', data['repositories'])
        print ('Followers: ', data['followers'])
        print ('Created at: ', data['created_at'])
        print ('Description: ', data['description'])
        print('--------------------\n')

        repo_count = int(data['repositories'])

        repos = self.fetch_repos(company, repo_count)
        contributors = fetch_contributors_for_company(company)

        self.company_ls.append([company, repo_count, contributors])
        self.company_ls.sort(key=lambda x: x[1], reverse=True)

        # show the sorted company by repo number
        self.display_companies()

        # show contribution matrix
        self.display_contributor_matrix()


if __name__ == '__main__':
    print('Fetch github organization data')
    spider = GithubSpider()
    # common company: alibaba, aws etc
    while True:
        company = input('\nInput the company name(in lower case, eg. google, microsoft, alibaba. Leave empty to exit): ')
        if not company:
            break
        spider.run(company)
