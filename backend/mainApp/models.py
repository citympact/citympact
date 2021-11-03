from django.db import models
from django.conf import settings
from PIL import Image

class CityProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1500)
    image = models.ImageField()
    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super(CityProject, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        img.thumbnail(settings.IMG_THUMBNAIL_SIZE)
        chunks = self.image.path.split(".")
        chunks[-2] += "_"+("x".join(
            [str(x) for x in settings.IMG_THUMBNAIL_SIZE]
        ))
        img.save(".".join(chunks))


class CityProjectVote(models.Model):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)
    comment = models.CharField(max_length=1500)
    def __str__(self):
        return "%d (%s)" % (self.vote, self.comment)
