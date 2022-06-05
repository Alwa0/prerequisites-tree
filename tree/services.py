import json
import re

import requests
import graphviz
from tree.models import Course, CourseRelations, Category


def find_courses(program):
    CourseRelations.objects.filter(prerequisite__program=program, from_eduwiki=True).delete()
    Course.objects.filter(program=program, from_eduwiki=True).delete()
    url = "https://eduwiki.innopolis.university/api.php"
    params = {}
    if program == "bach":
        params = {'pageid': '156', 'format': 'json', 'action': 'parse', 'prop': 'wikitext'}
    if program == "mast":
        params = {'pageid': '157', 'format': 'json', 'action': 'parse', 'prop': 'wikitext'}
    r = requests.get(url=url, params=params)
    try:
        data = r.json()
    except:
        return
    data = json.dumps(data)
    data = data.split("Unnumbered courses")[0]
    data = ' '.join(data.split())
    data = data.split('\\n*')[1:]
    data.pop(8)
    for i in range(len(data)):
        if data[i][0] != ' ':
            data[i] = ' ' + data[i]
    links = [c.split(' ')[1][1:] for c in data]
    course_ids = [c.split(' ')[2] for c in data]
    courses = [c.split(' ')[4:] for c in data]
    courses = [" ".join(c) for c in courses]
    i = 0
    for c in courses:
        if 'Elective' not in c:
            if ']' in c:
                name = c[:c.index(']')]
                course, _ = Course.objects.get_or_create(
                        name=name,
                        url=links[i],
                        course_id=course_ids[i],
                        program=program
                    )
                category = Category.objects.filter(course_ids=course.course_id[:4])
                if category.first():
                    course.category = category.first()
                    course.save()
        i += 1


def find_prerequisites(course):
    CourseRelations.objects.filter(post_name=course, from_eduwiki=False).update(
        post_requisite=course
    )
    CourseRelations.objects.filter(pre_name=course, from_eduwiki=False).update(
        prerequisite=course
    )
    if course.name[-3:] == " II" and (instance := Course.objects.filter(name=course.name[:-1]).first()):
        if not CourseRelations.objects.filter(prerequisite=instance, post_requisite=course).first():
            CourseRelations.objects.create(prerequisite=instance, pre_name=instance.name,
                                           post_requisite=course, post_name=course.name)
    page = course.url.split('/')[-1].split('.')[0]
    params = {"page": page, "action": "parse", "prop": "wikitext", "format": "json"}
    r = requests.get(url="https://eduwiki.innopolis.university/api.php", params=params)
    data = r.json()
    data = json.dumps(data)
    if "== Prerequisites ==" in data:
        prerequisites = data.split("== Prerequisites ==")[1].split("==")[0].split('\\n')
        while '' in prerequisites:
            prerequisites.remove('')
        pattern = r"^\*.{0,}\[\S*.\s{1}.{6}.{2,}\w\]"
        for p in prerequisites:
            if not re.match(pattern, p):
                continue
            pid = p.split(' ')[2]
            if Course.objects.filter(course_id=pid, program=course.program).first():
                edge = (Course.objects.get(course_id=pid), course)
                pre = Course.objects.get(name=edge[0], program=course.program)
                if not CourseRelations.objects.filter(prerequisite=pre, post_requisite=course).first():
                    CourseRelations.objects.create(prerequisite=pre, pre_name=pre.name,
                                                   post_requisite=course, post_name=course.name)


def create_graph(graph_format):
    graph = graphviz.Digraph(name='Prerequisites tree', format=graph_format)
    graph.node_attr['shape'] = 'rectangle'
    graph.node_attr['fixedsize'] = 'true'
    graph.node_attr['width'] = '1.2'
    graph.node_attr['height'] = '1'
    graph.node_attr['style'] = 'rounded, filled'
    graph.node_attr['fillcolor'] = 'azure2'
    graph.node_attr['fontcolor'] = 'black'
    graph.node_attr['fontsize'] = '11'
    graph.graph_attr['ranksep'] = '0.7'
    return graph


def split_string(name: str):
    result = name
    if len(name) > 16:
        result = ''
        words = name.split(' ')
        while len(words) > 0:
            row = ''
            while len(row) + len(words[0]) < 16:
                row += words.pop(0) + ' '
                if len(words) == 0:
                    break
            result += row
            result += '\n'
        result = result[:-1]
    return result


def check_relations(relation):
    pre = relation.prerequisite
    post = relation.post_requisite
    pre_rel = CourseRelations.objects.filter(prerequisite=pre)
    post_rel = CourseRelations.objects.filter(post_requisite=post)
    for f in pre_rel:
        for s in post_rel:
            if f.post_requisite == s.prerequisite or \
                    CourseRelations.objects.filter(prerequisite=f.post_requisite, post_requisite=s.prerequisite).first():
                relation.visible = False
                relation.save()
