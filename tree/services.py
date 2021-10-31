import json
import requests
import graphviz
from tree.models import Course, CourseRelations


def find_courses():
    Course.objects.all().delete()
    CourseRelations.objects.all().delete()
    url = "https://eduwiki.innopolis.university/api.php"
    params = {'pageid': '156', 'format': 'json', 'action': 'parse', 'prop': 'wikitext'}
    r = requests.get(url=url, params=params)
    data = r.json()
    data = json.dumps(data)
    data = data.split('\\n*')[1:]
    links = [c.split(' ')[1][1:] for c in data]
    courses = [c.split(' ')[2:] for c in data]
    courses = [" ".join(c) for c in courses]
    i = 0
    for c in courses:
        if 'Elective' not in c:
            if ']' in c:
                name = c[:c.index(']')]
                if not Course.objects.filter(name=name).first():
                    Course.objects.create(name=name, url=links[i])
        i += 1


def find_prerequisites(course):
    CourseRelations.objects.filter(post_requisite=course).delete()
    if course.name[-3:] == " II" and (instance := Course.objects.filter(name=course.name[:-1]).first()):
        if not CourseRelations.objects.filter(prerequisite=instance, post_requisite=course).first():
            CourseRelations.objects.create(prerequisite=instance, post_requisite=course)
    page = course.url.split('/')[-1]
    params = {"page": page, "action": "parse", "prop": "wikitext", "format": "json"}
    r = requests.get(url="https://eduwiki.innopolis.university/api.php", params=params)
    data = r.json()
    data = json.dumps(data)
    if "Prerequisites" in data:
        params = {"page": page, "action": "parse", "prop": "wikitext", "format": "json"}
        r = requests.get(url="https://eduwiki.innopolis.university/api.php", params=params)
        data = r.json()
        data = json.dumps(data)
        prerequisites = data.split("== Prerequisites ==")[1].split("==")[0].split('\\n')
        while '' in prerequisites:
            prerequisites.remove('')
        prerequisites = [p[2:] for p in prerequisites]
        for p in prerequisites:
            edge = None
            if Course.objects.filter(name=p.title()).first():
                edge = (p.title(), course)
            elif Course.objects.filter(name=p.title()[:-1]+"I").first():
                edge = (p.title()[:-1]+"I", course)
            elif p == "Discrete Math/Logic" or p == "Discrete Math and Logic":
                edge = ("Philosophy I", course)
            elif p == "Data Structure and Algorithms I":
                edge = ("Data Structures Algorithms I", course)
            elif p == "Data Structure and Algorithms II":
                edge = ("Data Structures Algorithms II", course)
            if edge:
                pre = Course.objects.get(name=edge[0])
                if not CourseRelations.objects.filter(prerequisite=pre, post_requisite=course).first():
                    CourseRelations.objects.create(prerequisite=pre, post_requisite=course)


def create_graph(graph_format):
    graph = graphviz.Digraph(name='Prerequisites tree', format=graph_format)
    graph.node_attr['shape'] = 'circle'
    graph.node_attr['fixedsize'] = 'true'
    graph.node_attr['width'] = '1.5'
    graph.node_attr['style'] = 'filled'
    graph.node_attr['fillcolor'] = 'coral1'
    graph.node_attr['fontcolor'] = 'black'
    graph.node_attr['fontsize'] = '12'
    graph.graph_attr['ranksep'] = '2'
    return graph
