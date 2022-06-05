from django.db import models


class Category(models.Model):
    course_ids = models.CharField(max_length=5, blank=False, null=False)
    name = models.CharField(max_length=500, blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.course_ids + ": " + self.name


class Course(models.Model):
    name = models.CharField(max_length=500)
    url = models.CharField(max_length=500, default=None, null=True)
    course_id = models.CharField(max_length=6, default=None, null=True)
    program = models.CharField(max_length=10, default=None, null=True)
    from_eduwiki = models.BooleanField(default=True, null=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class CourseRelations(models.Model):
    pre_name = models.CharField(max_length=500, default=None, null=True)
    prerequisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="prerequisite")
    post_name = models.CharField(max_length=500, default=None, null=True)
    post_requisite = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="post_requisite")
    from_eduwiki = models.BooleanField(default=True, null=True)
    visible = models.BooleanField(default=True, null=False)

    class Meta:
        unique_together = ('prerequisite', 'post_requisite',)

    def __str__(self):
        return self.prerequisite.name + " -> " + self.post_requisite.name
