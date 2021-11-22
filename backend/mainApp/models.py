from django.db import models
from django.contrib.sessions.models import Session
from django.conf import settings
from PIL import Image


def createThumbnail(imagePath):
    img = Image.open(imagePath)
    img.thumbnail(settings.IMG_THUMBNAIL_SIZE)
    chunks = imagePath.split(".")
    chunks[-2] += "_"+("x".join(
        [str(x) for x in settings.IMG_THUMBNAIL_SIZE]
    ))
    img.save(".".join(chunks))

class CityProject(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField()
    image = models.ImageField()
    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super(CityProject, self).save(*args, **kwargs)
        if self.image is not None:
            createThumbnail(self.image.path)


class CityProjectVote(models.Model):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)
    comment = models.TextField()
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_project_vote_per_session',
                fields=['project', "session"],
            )
        ]

    def __str__(self):
        return ("blank vote" if self.vote==0 else \
            "up vote" if self.vote>0 else "down vote")\
            + " (%s)" % self.session.session_key


class Petition(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    #"author":
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super(Petition, self).save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            createThumbnail(self.image.path)

class RegisteredUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    zip_code = models.DecimalField(max_digits=10, decimal_places=0)
    city = models.CharField(max_length=254)
    birth_year = models.DecimalField(max_digits=4, decimal_places=0)



class PetitionSignature(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
