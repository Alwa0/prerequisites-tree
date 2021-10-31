import json

import requests


def find_prerequisites(courses):
    url = "https://eduwiki.innopolis.university/api.php"
    edges = []
    for course in courses:
        if course[-2:] == " I" and course + "I" in courses:
            edge = (course, course + "I")
            if edge not in edges:
                edges.append(edge)
        page = courses[course].split('/')[-1]
        params = {"page": page, "action": "parse", "prop": "wikitext", "format": "json"}
        r = requests.get(url=url, params=params)
        data = r.json()
        data = json.dumps(data)
        if "Prerequisites" in data:
            params = {"page": page, "action": "parse", "prop": "wikitext", "format": "json"}
            r = requests.get(url=url, params=params)
            data = r.json()
            data = json.dumps(data)
            prerequisites = data.split("== Prerequisites ==")[1].split("==")[0].split('\\n')
            while '' in prerequisites:
                prerequisites.remove('')
            prerequisites = [p[2:] for p in prerequisites]
            for p in prerequisites:
                if p.title() in courses:
                    edge = (p.title(), course)
                elif p.title()[:-1]+"I" in courses:
                    edge = (p.title()[:-1]+"I", course)
                elif p == "Discrete Math/Logic" or p == "Discrete Math and Logic":
                    edge = ("Philosophy I", course)
                elif p == "Data Structure and Algorithms I":
                    edge = ("Data Structures Algorithms I", course)
                elif p == "Data Structure and Algorithms II":
                    edge = ("Data Structures Algorithms II", course)
                if edge not in edges:
                    edges.append(edge)

    return edges
