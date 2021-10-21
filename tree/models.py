from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=500)
    topics = models.ManyToManyField(Topic)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.name


class CourseRelations(models.Model):
    prerequisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="prerequisite")
    post_requisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="post_requisite")

    def __str__(self):
        return self.prerequisite.name + " -> " + self.post_requisite.name

