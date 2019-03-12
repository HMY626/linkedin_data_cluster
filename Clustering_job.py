# -*- coding:utf-8 -*-
import os
import csv
import json
import re
import random
from nltk.metrics.distance import jaccard_distance

DISTANCE_THRESHOLD = 0.45
DISTANCE = jaccard_distance

def cluster_contacts_by_title(JSON_FILE):

    transforms = [
        ('Sr.', 'Senior'),
        ('Sr', 'Senior'),
        ('Jr.', 'Junior'),
        ('Jr', 'Junior'),
        ('CEO', 'Chief Executive Officer'),
        ('COO', 'Chief Operating Officer'),
        ('CTO', 'Chief Technology Officer'),
        ('CFO', 'Chief Finance Officer'),
        ('VP', 'Vice President'),
        ]


    with open(JSON_FILE, 'r') as f:
        dataset = json.load(f)

    all_titles = []
    for p in dataset:
        if p.has_key('events'):
            titles = []
            if len(p['events']) > 0:
                for e in p['events']:
                    titles.append(e['title1'])
                    titles.append(e['title2'])
        else:
            continue

        for title in titles:
            if re.search('/| and |&', title):
                titles.remove(title)
                titles.extend([t.strip() for t in re.split('/| and |&', title)  if t.strip() != ''])

        for transform in transforms:
            titles = [title.replace(*transform) for title in titles]
        all_titles.extend(titles)

    all_titles = list(set(all_titles))
    #print all_titles
    print len(all_titles)

    clusters = {}
    for title1 in all_titles:
        clusters[title1] = []
        for sample in range(100):
            title2 = all_titles[random.randint(0, len(all_titles)-1)]
            if title2 in clusters[title1] or clusters.has_key(title2) and title1 in clusters[title2]:
                continue
            distance = DISTANCE(set(title1.split()), set(title2.split()))
            if distance < DISTANCE_THRESHOLD:
                clusters[title1].append(title2)

    clusters = [clusters[title] for title in clusters if len(clusters[title]) > 1]

    clustered_contacts = {}
    for cluster in clusters:
        clustered_contacts[tuple(cluster)] = []
        for p in dataset:
            if p.has_key('events'):
                for event in p['events']:
                    if event['title1'] or event['title2'] in cluster:
                        clustered_contacts[tuple(cluster)].append('%s %s' % (p['name']['given_name'], p['name']['family_name']))

        clustered_contacts[tuple(cluster)] = list(set(clustered_contacts[tuple(cluster)]))
    return clustered_contacts

clustered_contacts = cluster_contacts_by_title('linkedin_lite_data.json')
#print clustered_contacts
for titles in clustered_contacts:
    common_titles_heading = 'Common Titles: ' + ', '.join(titles)

    descriptive_terms = set(titles[0].split())
    for title in titles:
        descriptive_terms.intersection_update(set(title.split()))
    descriptive_terms_heading = 'Descriptive Terms: ' \
            + ', '.join(descriptive_terms)
    print descriptive_terms_heading
    print '-' * max(len(descriptive_terms_heading), len(common_titles_heading))
    print '\n'.join(clustered_contacts[titles][-10:])
    print