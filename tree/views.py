import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, Http404, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tree.services import find_prerequisites, create_graph, find_courses, split_string, check_relations
from tree.models import CourseRelations, Course, Category


def tree(request, program, visible=0):
    if request.method == "POST" \
            or not CourseRelations.objects.filter(prerequisite__program=program, from_eduwiki=True).first():
        find_courses(program)
        for course in Course.objects.filter(program=program, from_eduwiki=True):
            find_prerequisites(course)
        relations = CourseRelations.objects.all()
        for relation in relations:
            check_relations(relation)
    graph = create_graph('svg')
    for course in Course.objects.filter(program=program):
        n = split_string(course.name)
        color = 'beige'
        if Category.objects.filter(course_ids=course.course_id[:4]).first():
            color = Category.objects.get(course_ids=course.course_id[:4]).color
        graph.node(n, URL=course.url, fillcolor=color, color="grey44")
    edges = CourseRelations.objects.filter(prerequisite__program=program)
    for edge in edges:
        n1 = split_string(edge.prerequisite.name)
        n2 = split_string(edge.post_requisite.name)
        if edge.visible or visible:
            graph.edge(n1, n2, color='grey44')
    data = graph.pipe().decode('utf-8') + "<br><br>"
    categories = Category.objects.all()

    center = (len(categories) + 1) // 2
    if len(categories) % 2 == 0:
        center = len(categories) // 2 + 1

    # Legend
    data += """<div style="display: inline-block; margin:10px; vertical-align: top;">"""
    for category in categories[0:center]:
        num = len(Course.objects.filter(category=category, program=program))
        data += f"""
        <div style="margin: 2px;">
            <div style="
                display: inline-block;
                position: relative;
                background-color: {category.color};
                border-radius: 12px;
                border: solid 1px black;
                height: 15px;
                width: 15px;
                top: 2px;
            "></div>
            {category.name}({num})
        </div>"""
    data += "</div>"
    data += """<div style="display: inline-block; margin:10px; vertical-align: top;">"""
    for category in categories[center:]:
        num = len(Course.objects.filter(category=category, program=program))
        data += f"""
        <div style="margin: 2px;">
            <div style="
                display: inline-block;
                position: relative;
                background-color: {category.color};
                border-radius: 12px;
                border: solid 1px black;
                height: 15px;
                width: 15px;
                top: 2px;
            "></div>
            {category.name}({num})
        </div>"""
    data += "</div>"

    # buttons
    data += """\n
    <div>
    <form action="{% url 'tree' '""" + program + """' """ + str(int(not visible)) +"""  %}" method="get"
        style="display: inline-block; margin:10px; vertical-align: top;"
    >
        <button type="submit" style="
            background-color: rgb(224,238,238); 
            border: solid 1px darkslategrey; 
            border-radius: 12px;
            height: 50px;
            width: 100px;
            font-size: 15px;
            cursor: pointer;
        ">Change format</button>
    </form>
    <form action="{% url 'tree' '""" + program + """' """ + str(visible) +"""  %}" method="post"
        style="display: inline-block; margin:10px; vertical-align: top;"
    >
        {% csrf_token %}
        <button type="submit" style="
            background-color: rgb(224,238,238); 
            border: solid 1px darkslategrey; 
            border-radius: 12px;
            height: 50px;
            width: 100px;
            font-size: 15px;
            cursor: pointer;
        ">Update</button>
    </form>
    <form action="{% url 'choose program' %}" method="get" 
        style="display: inline-block; margin:10px; vertical-align: top;"
    >
        {% csrf_token %}
        <button type="submit" style="
            background-color: rgb(224,238,238); 
            border: solid 1px darkslategrey; 
            border-radius: 12px;
            height: 50px;
            width: 100px;
            font-size: 15px;
            cursor: pointer;
        ">Edit prerequisites</button>
    </form>
    </div>
    """

    f = open("templates/tree/tree.html", 'w+')
    f.write(data)
    return render(request, "tree/tree.html")


@api_view(('GET',))
def graph_for_course(request, course_name):
    cn = split_string(course_name)
    graph = create_graph('json')
    course = get_object_or_404(Course, name=course_name)
    graph.node(cn, URL=course.url)
    pres = CourseRelations.objects.filter(post_requisite=course)
    posts = CourseRelations.objects.filter(prerequisite=course)
    for pre in pres:
        n = split_string(pre.prerequisite.name)
        graph.node(n, URL=pre.prerequisite.url)
        graph.edge(n, cn)
    for post in posts:
        n = split_string(post.post_requisite.name)
        graph.node(n, URL=post.post_requisite.url)
        graph.edge(cn, n)
    data = graph.pipe().decode('utf-8')
    data = json.loads(data)
    return Response(data)


@api_view(('GET',))
def graph_for_course_id(request, course_id):
    graph = create_graph('json')
    course = get_object_or_404(Course, course_id=course_id)
    graph.node(course.name, URL=course.url)
    pres = CourseRelations.objects.filter(post_requisite=course)
    posts = CourseRelations.objects.filter(prerequisite=course)
    for pre in pres:
        n = split_string(pre.prerequisite.name)
        graph.node(n, URL=pre.prerequisite.url)
        graph.edge(n, course.name)
    for post in posts:
        n = split_string(post.post_requisite.name)
        graph.node(n, URL=post.post_requisite.url)
        graph.edge(course.name, n)
    data = graph.pipe().decode('utf-8')
    data = json.loads(data)
    return Response(data)


def show_graph_for_course(request, course_name):
    request = HttpRequest()
    request.method = 'GET'
    response = graph_for_course(request, course_name)
    if response.status_code != 200:
        raise Http404("No such course")
    data = response.data
    nodes = data['objects']
    edges = []
    if 'edges' in data:
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


@csrf_exempt
def choose_prerequisites(request, program, course):
    if request.method == "POST":
        post_requisite = get_object_or_404(Course, name=course, program=program)
        CourseRelations.objects.filter(post_requisite=post_requisite).delete()
        for pre in list(request.POST)[:-1]:
            if not CourseRelations.objects.filter(prerequisite__name=pre, post_requisite__name=course).first():
                prerequisite = get_object_or_404(Course, name=pre, program=program)
                CourseRelations.objects.create(
                    prerequisite=prerequisite,
                    pre_name=prerequisite.name,
                    post_requisite=post_requisite,
                    post_name=post_requisite.name,
                    from_eduwiki=False
                )
        if request.POST['others'] != '':
            others = request.POST['others'].split(', ')
            for pre in others:
                c = Course.objects.create(name=pre, program=program, from_eduwiki=False)
                c.course_id = c.id
                c.save()
                CourseRelations.objects.create(prerequisite=c, pre_name=pre,
                                               post_requisite=post_requisite, post_name=course,
                                               from_eduwiki=False)
        return redirect('tree', program=program)
    else:
        prerequisites = Course.objects.filter(program=program).exclude(name=course).order_by('name').values_list('name')
        pre_list = [c[0] for c in list(prerequisites)]
        center = (len(pre_list) + 1) // 2
        if len(pre_list) % 2 == 0:
            center = len(pre_list) // 2 + 1
        pre_list1 = pre_list[:center]
        pre_list2 = pre_list[center:]

        chosen = list(CourseRelations.objects.filter(
            post_requisite__name=course,
            post_requisite__program=program
        ).values_list('pre_name'))
        chosen_list = [c[0] for c in chosen]
        return render(request, 'prerequisites.html', {
            'program': program,
            'course': course,
            'prerequisites1': pre_list1,
            'prerequisites2': pre_list2,
            'chosen': chosen_list
        })


@csrf_exempt
def choose_program(request):
    if request.method == "POST":
        if 'bachelor' in request.POST:
            return redirect('choose course', program='bach')
        elif 'master' in request.POST:
            return redirect('choose course', program='mast')
        else:
            return HttpResponseNotFound('No such program')
    else:
        programs = ['bachelor', 'master']
        return render(request, 'programs.html', {'programs': programs})


@csrf_exempt
def choose_course(request, program):
    if request.method == "POST":
        course = request.POST["course"]
        return redirect('choose prerequisites', program=program, course=course)
    else:
        courses = Course.objects.filter(program=program).order_by('name')
        return render(request, 'courses.html', {'courses': courses})


@api_view(('GET',))
def graph_by_id(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    pres = CourseRelations.objects.filter(post_requisite=course)
    posts = CourseRelations.objects.filter(prerequisite=course)
    pres = [{
        "ID": pre.prerequisite.course_id,
        "name": pre.prerequisite.name,
        "url": pre.prerequisite.url
    } for pre in pres]
    posts = [{
        "ID": post.post_requisite.course_id,
        "name": post.post_requisite.name,
        "url": post.post_requisite.url
    } for post in posts]
    course = {"ID": course.course_id, "name": course.name, "url": course.url}
    data = {'course': course, 'prerequisites': pres, 'post_requisites': posts}
    return Response(data)


@api_view(('POST',))
def graph_for_student(request):
    json_data = request.data
    program = json_data['program']
    courses = json_data['courses']
    nodes = []
    edges = []
    for course in Course.objects.filter(program=program):
        node = {"id": course.course_id, "name": course.name, "URL": course.url, "fillcolor": "beige", "color": "grey44"}
        if Category.objects.filter(course_ids=course.course_id[:4]).first():
            node['fillcolor'] = Category.objects.get(course_ids=course.course_id[:4]).color
        if course.course_id in courses:
            node["color"] = "black"
        nodes.append(node)
    for edge in CourseRelations.objects.filter(prerequisite__program=program):
        pre = edge.prerequisite.course_id
        post = edge.post_requisite.course_id
        if pre in courses and post in courses:
            edges.append({"tail": pre, "head": post, "color": "black"})
        else:
            edges.append({"tail": pre, "head": post, "color": "grey44"})
    response = {"nodes": nodes, "edges": edges}
    return Response(response)
