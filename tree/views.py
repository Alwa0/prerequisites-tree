import graphviz

from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

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
    success = False
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
