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


class BaseModel(models.Model):
    create_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Visitor(BaseModel):
    def __str__(self):
        return "Visitor (%d)" % self.pk


class RegisteredUser(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    zip_code = models.DecimalField(max_digits=10, decimal_places=0)
    city = models.CharField(max_length=254)
    birth_year = models.DecimalField(max_digits=4, decimal_places=0)
    

class CityProject(BaseModel):
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


class CityProjectVote(BaseModel):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)
    comment = models.TextField()
    visitor = models.ForeignKey(Visitor, on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_project_vote_per_visitor',
                fields=['project', "visitor"],
            )
        ]

    def __str__(self):
        return ("blank vote" if self.vote==0 else \
            "up vote" if self.vote>0 else "down vote")\
            + " (%s)" % self.visitor.pk


class Petition(BaseModel):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    #"author":
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING,
        null=True, db_constraint=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super(models.Model, self).save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            createThumbnail(self.image.path)




class PetitionSignature(BaseModel):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING,
        null=True, db_constraint=False)
