import json
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tree.services import find_prerequisites, create_graph, find_courses
from tree.models import CourseRelations, Course


def tree(request):
    if request.method == "POST" or not CourseRelations.objects.first():
        find_courses()
        for course in Course.objects.all():
            find_prerequisites(course)
    graph = create_graph('svg')
    for course in Course.objects.all():
        n = course.name
        if len(n) > 15:
            n = n.replace(' ', '\n')
        graph.node(n, URL=course.url)
    edges = CourseRelations.objects.all()
    for edge in edges:
        n1 = edge.prerequisite.name
        n2 = edge.post_requisite.name
        if len(n1) > 15:
            n1 = n1.replace(' ', '\n')
        if len(n2) > 15:
            n2 = n2.replace(' ', '\n')
        graph.edge(n1, n2)
    data = graph.pipe().decode('utf-8')

    data += """\n
    <form action="{% url 'tree' %}" method="post">
        {% csrf_token %}
        <button type="submit" style="
            background-color: rgb(255,114,86); 
            border: solid 1px black; 
            border-radius: 50px;
            height: 50px;
            width: 100px;
            position: relative;
            top: 50px;
            left: 50px;
            font-size: 15px;
            cursor: pointer;
        ">Update</button>
    </form>
    """

    f = open("templates/tree/tree.html", 'w+')
    f.write(data)
    return render(request, "tree/tree.html")


@api_view(('GET',))
def graph_for_course(request, course_name):
    cn = course_name
    if len(cn) > 15:
        cn = cn.replace(' ', '\n')
    graph = create_graph('json')
    course = get_object_or_404(Course, name=course_name)
    graph.node(cn, URL=course.url)
    pres = CourseRelations.objects.filter(post_requisite=course)
    posts = CourseRelations.objects.filter(prerequisite=course)
    for pre in pres:
        n = pre.prerequisite.name
        if len(n) > 15:
            n = n.replace(' ', '\n')
        graph.node(n, URL=pre.prerequisite.url)
        graph.edge(n, cn)
    for post in posts:
        n = post.post_requisite.name
        if len(n) > 15:
            n = n.replace(' ', '\n')
        graph.node(n, URL=post.post_requisite.url)
        graph.edge(cn, n)
    data = graph.pipe().decode('utf-8')
    data = json.loads(data)
    return Response(data)


@api_view(('GET',))
def show_graph_for_course(request, course_name):
    response = graph_for_course(request._request, course_name)
    data = response.data
    nodes = data['objects']
    edges = data['edges']
    graph = create_graph('svg')
    for node in nodes:
        graph.node(node["name"], URL=node['URL'])
    for edge in edges:
        graph.edge(nodes[edge["tail"]]['name'], nodes[edge["head"]]['name'])
    data = graph.pipe().decode('utf-8')
    f = open("templates/tree/tree.html", 'w+')
    f.write(data)
    f.close()
    return render(request, 'tree/tree.html')
