import json

import graphviz

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
import requests

from tree.services import find_prerequisites
from tree.models import CourseRelations, Course, Section, Topic


def tree(request):
    graph = graphviz.Digraph(comment='Prerequisites tree', format='svg')
    nodes = Course.objects.all()
    for node in nodes:
        graph.node(node.name, URL=f"http://127.0.0.1:8000/{node.id}")
    edges = CourseRelations.objects.all()
    for edge in edges:
        pre = edge.prerequisite
        post = edge.post_requisite
        graph.edge(pre.name, post.name)

    graph.node_attr['shape'] = 'circle'
    graph.node_attr['fixedsize'] = 'true'
    graph.node_attr['width'] = '1.5'
    graph.node_attr['style'] = 'filled'
    graph.node_attr['fillcolor'] = 'coral1'
    graph.node_attr['fontcolor'] = 'black'
    graph.node_attr['fontsize'] = '12'
    graph.graph_attr['ranksep'] = '2'
    # graph.render("output/graph.gv", view=True)
    data = graph.pipe().decode('utf-8')

    f = open("templates/tree/tree.html", 'w')
    f.write(data)
    return render(request, "tree/tree.html")


def get_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    sections = course.sections.all()
    topics = {}
    for section in sections:
        topics[section.name] = section.topics.all()
    return render(request, "tree/course.html", {"topics": topics, "sections": sections})


@csrf_protect
def add_sections_and_topics(request):
    if request.method == 'POST':
        course_id = request.POST['course']
        course = get_object_or_404(Course, id=course_id)
        data = request.POST['data']
        data = data.replace("\r\n    ", "$")
        sections = data.split("\r\n")
        ss = []
        for section in sections:
            topics = section.split('$')
            section = topics.pop(0)
            ts = []
            for topic in topics:
                t = Topic.objects.create(name=topic)
                ts.append(t)
            s = Section.objects.create(name=section)
            s.topics.set(ts)
            ss.append(s)
        course.sections.set(ss)
    courses = Course.objects.all()
    return render(request, "tree/add-sections-topics.html",
                  context={"courses": courses})


def courses_from_edu(request):
    url = "https://eduwiki.innopolis.university/api.php"
    params = {'pageid': '156', 'format': 'json', 'action': 'parse', 'prop': 'wikitext'}
    r = requests.get(url=url, params=params)
    data = r.json()
    data = json.dumps(data)
    data = data.split('\\n*')[1:]
    links = [c.split(' ')[1][1:] for c in data]
    courses = [c.split(' ')[2:] for c in data]
    courses = [" ".join(c) for c in courses]
    names = {}
    i = 0
    for c in courses:
        if 'Elective' not in c:
            if ']' in c:
                name = c[:c.index(']')]
                if name not in names:
                    names[name] = links[i]
            else:
                names[c] = links[i]
        i += 1
    graph = graphviz.Digraph(comment='Prerequisites tree', format='svg')
    for name in names.keys():
        n = name
        if len(name) > 15:
            n = name.replace(' ', '\n')
        graph.node(n, URL=names[name])
    edges = find_prerequisites(names)
    print(edges)
    for edge in edges:
        n1 = edge[0]
        n2 = edge[1]
        if len(n1) > 15:
            n1 = n1.replace(' ', '\n')
        if len(n2) > 15:
            n2 = n2.replace(' ', '\n')
        graph.edge(n1, n2)
    graph.node_attr['shape'] = 'circle'
    graph.node_attr['fixedsize'] = 'true'
    graph.node_attr['width'] = '1.5'
    graph.node_attr['style'] = 'filled'
    graph.node_attr['fillcolor'] = 'coral1'
    graph.node_attr['fontcolor'] = 'black'
    graph.node_attr['fontsize'] = '12'
    graph.graph_attr['ranksep'] = '2'
    # graph.render("output/graph.gv", view=True)
    data = graph.pipe().decode('utf-8')

    f = open("templates/tree/tree.html", 'w')
    f.write(data)
    return render(request, "tree/tree.html")
