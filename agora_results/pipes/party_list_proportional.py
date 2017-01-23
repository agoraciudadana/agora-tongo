# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2017  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import operator

def enma_2(data_list, question_indexes=None, women_names=None):
    '''
    This is a party-list proportional representation method needed for the
    electoral process named ENMA-2. When there is a seat in dispute between
    multiple lists, the seat is given to the party with the higher decimal
    number.

    This function assumes that:
     - the question has been already tallied with plurality-at-large, and thus
       merely calculates the winner_position of the candidates.
     - the candidates include Gender in their URLs.
     - the candidates are ordered by list order.
    '''
    data = data_list[0]

    for qindex, question in enumerate(data['results']['questions']):
        # filter questions we want only
        if question_indexes is not None and qindex not in question_indexes:
            continue

        num_winners = question['num_winners']
        total_votes = question['totals']['valid_votes']

        # first sort by category, then group by category, then convert into a
        # dict with key being the category, the value being a list of options
        question['answers'].sort(key=operator.itemgetter('category'))
        answers_grouped = itertools.groupby(question['answers'], operator.itemgetter('category'))
        lists_data = dict()

        def seats(list_points):
            '''
            Calculates the number of seats that belong to a party
            proportionally to their number of votes, without assigning any
            seat that is in dispute with any other party.
            '''
            return float(num_winners * list_points) / total_votes

        def fraction_points(list_points):
            '''
            Calculates the decimal part of the points over the total votes for
            a list.
            '''
            val = float(list_points) / total_votes
            return val - int(val)

        for cat, cat_answers in answers_grouped:
            cat_answers = list(cat_answers)
            lists_data[cat] = dict(
                points=cat_answers[0]['total_count'],
                seats=int(seats(cat_answers[0]['total_count'])),
                fraction_points=fraction_points(cat_answers[0]['total_count']),
                answers=cat_answers,
                cat_name=cat
            )

        # this is the number of seats in dispute
        given_seats = sum(map(operator.itemgetter('seats'), lists_data.values()))
        disputed_seats = num_winners - given_seats
        lists_l = list(lists_data.values())
        lists_l.sort(key=operator.itemgetter('fraction_points'), reverse=True)

        # give disputed seats
        for i in range(disputed_seats):
            lists_l[i]['seats'] += 1

        # finally, mark winners per list
        winner_pos = 0
        for l in lists_l:
            if len(l['answers']) < l['seats']:
                print("giving to list %s only %d seats (all candidates) instead of %d" % (
                    l['cat_name'], len(l['answers']), l['seats']))
                l['seats'] = len(l['answers'])
            for i, answer in enumerate(l['answers']):
                if i < l['seats']:
                    answer['winner_position'] = winner_pos
                    winner_pos += 1
                else:
                    answer['winner_position'] = None

        def filter_women(l, women_names):
          return [a for a in l if a['text'] in women_names and a['winner_position'] is not None]
        def filter_men(l, women_names):
          return [a for a in l if a['text'] not in women_names and a['winner_position'] is not None]

        women = filter_women(question['answers'], women_names)
        men = filter_men(question['answers'], women_names)

        # if there are too many men, then we take out the last elected man of the
        # list elected with less votes and insert the first not-elected woman in
        # from that list

        if len(women) <= len(men):
            print("too many men")
            lists_l.sort(key=operator.itemgetter('points'), reverse=False)
            if lists_l[0]['points'] == lists_l[1]['points']:
                print("Oops, we need to take back last man seat from the least voted list to give it to the next woman, but there's a tie in the number of points of the first two lists")
            l = lists_l[0]
            total = l['seats']
            l['answers'][total-1]['winner_position'] = None
            if len(l['answers']) > total:
                l['answers'][total]['winner_position'] = total-1
            else:
                print("not assigning the seat #%d because the list doesn't have any more women" % (total-1))

if __name__ == '__main__':
    '''
    executes some unittests in here.
    '''
    def generate_test_data():
        '''
        Given a string of sexes in order (for example "HHHMMH"), generates a test
        election data to be used with podemos_parity_loreg_zip_non_iterative.
        '''
        q = {
          "tally_type": "plurality-at-large",
          "num_winners": 3,
          "totals": {
              "valid_votes": 65
          },
          "answers": [
          {
            "id": 0,
            "category": "c1",
            "details": "",
            "total_count": 30,
            "sort_order": 0,
            "urls": [
              {
                "title": "URL",
                "url": ""
              },
              {
                "title": "Image URL",
                "url": ""
              },
              {
                "title": "Gender",
                "url": "https://agoravoting.com/api/Gender/M"
              }
            ],
            "text": "a - c1.1 - M"
          },
          {
            "id": 1,
            "category": "c1",
            "details": "",
            "sort_order": 1,
            "urls": [
              {
                "title": "URL",
                "url": ""
              },
              {
                "title": "Image URL",
                "url": ""
              },
              {
                "title": "Gender",
                "url": "https://agoravoting.com/api/Gender/H"
              }
            ],
            "text": "b - c1.2 - H"
          },
          {
            "category": "c1",
            "details": "",
            "id": 2,
            "sort_order": 2,
            "text": "c - c1.3 - M",
            "urls": [
              {
                "title": "URL",
                "url": ""
              },
              {
                "title": "Image URL",
                "url": ""
              },
              {
                "title": "Gender",
                "url": "https://agoravoting.com/api/Gender/M"
              }
            ]
          },
          {
            "category": "c2",
            "details": "",
            "id": 3,
            "total_count": 35,
            "sort_order": 3,
            "text": "d - c2.1 - M",
            "urls": [
              {
                "title": "URL",
                "url": ""
              },
              {
                "title": "Image URL",
                "url": ""
              },
              {
                "title": "Gender",
                "url": "https://agoravoting.com/api/Gender/M"
              }
            ]
          },
          {
            "category": "c2",
            "details": "",
            "id": 4,
            "sort_order": 4,
            "text": "e - c2.2 - H",
            "urls": [
              {
                "title": "URL",
                "url": ""
              },
              {
                "title": "Image URL",
                "url": ""
              },
              {
                "title": "Gender",
                "url": "https://agoravoting.com/api/Gender/H"
              }
            ]
          }
        ],
        }

        return {
          "results": {
            "questions": [q]
          }
        }

    enma_2([generate_test_data()])