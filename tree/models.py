from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.CharField(max_length=500, unique=True, default=None)

    def __str__(self):
        return self.name


class CourseRelations(models.Model):
    prerequisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="prerequisite")
    post_requisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="post_requisite")

    class Meta:
        unique_together = ('prerequisite', 'post_requisite',)

    def __str__(self):
        return self.prerequisite.name + " -> " + self.post_requisite.name

