from django.db import models

class CityProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1500)
    image = models.ImageField()
    def __str__(self):
        return self.title


class CityProjectVote(models.Model):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)
    comment = models.CharField(max_length=1500)
    def __str__(self):
        return "%d (%s)" % (self.vote, self.comment)
