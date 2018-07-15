#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import xml.dom.minidom


def generate_opml(mydict):
    doc = xml.dom.minidom.Document()
    opml = doc.createElement('opml')
    opml.setAttribute('version', '2.0')
    doc.appendChild(opml)
    head = doc.createElement('head')
    opml.appendChild(head)
    title = doc.createElement('title')
    title.appendChild(doc.createTextNode(str(mydict['title'])))
    head.appendChild(title)
    body = doc.createElement('body')
    d = mydict['body']
    body = generate_nodes(d, doc, body)
    opml.appendChild(body)
    return doc


def generate_nodes(mydict, doc, root=None):
    if not root:
        root = doc.createElement('outline')
        root.appendChild(doc.createTextNode('dummy'))
    for k in mydict.keys():
        outline = doc.createElement('outline')
        outline.setAttribute('text', k)
        root.appendChild(outline)
        v = mydict.get(k)
        if len(v.keys()) > 0:
            generate_nodes(v, doc, outline)
    return root


def align_df(df):
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')
    df = df.reset_index(drop=True)
    m, n = df.shape
    i = 0
    while i < n - 1:
        s = df.iloc[:, i]
        arr_na = pd.isnull(s)
        df.iloc[:, i] = s.fillna(method='ffill')
        df = df.iloc[list(arr_na), :]
        i = i + 1
    return df


def nesting_dict_by_list(list_, dict_):
    nested_dict = dict()
    key = list_[0]
    if key in dict_.keys():
        nested_dict = dict_[key]
    else:
        dict_.update({key: nested_dict})
    if len(list_) == 1:
        return dict_
    else:
        nesting_dict_by_list(list_[1:], nested_dict)


def csv2opml(filename):
    basename = os.path.basename(filename)
    title = basename.split('.')[0]
    mydict = dict()
    mydict.update({'title': title})
    csv = pd.read_csv(filename, header=-1)
    csv = align_df(csv)
    m, _ = csv.shape
    body = dict()
    for i in range(m):
        row = [str(x) for x in csv.iloc[i, :].dropna().tolist()]
        nesting_dict_by_list(list_=row, dict_=body)
    mydict.update({'body': body})
    doc = generate_opml(mydict)
    new_filename = '.'.join([filename.split('.')[0], 'opml'])
    with open(new_filename, 'w') as f:
        doc.writexml(
            f, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    return True


if __name__ == '__main__':
    fn = sys.argv[1]
    print(csv2opml(fn))
