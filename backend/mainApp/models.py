from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sessions.models import Session
from django.db import models

from PIL import Image


def createThumbnail(imagePath):
    img = Image.open(imagePath)
    img.thumbnail(settings.IMG_THUMBNAIL_SIZE)
    chunks = imagePath.split(".")
    chunks[-2] += "_"+("x".join(
        [str(x) for x in settings.IMG_THUMBNAIL_SIZE]
    ))
    img.save(".".join(chunks))


class UserTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


class BaseModel(models.Model):
    create_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Visitor(BaseModel):
    def __str__(self):
        return "Visitor (%d)" % self.pk

class RegisteredUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    MANUALLY_CREATED = "MANUALLY_CREATED"
    registration_provider = models.CharField(max_length=254)

    zip_code = models.DecimalField(max_digits=10, decimal_places=0, null=True)
    city = models.CharField(max_length=254, null=True)
    birth_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)

    def __str__(self):
        return str(self.user)

class CityProject(BaseModel):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField()
    image = models.ImageField()
    views = models.IntegerField(default=0)

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


class CityProjectAdditionalImage(BaseModel):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return "Image aditionnelle au projet - %s" % self.project

    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super(CityProjectAdditionalImage, self).save(*args, **kwargs)
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


class CityProjectComment(BaseModel):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    visitor = models.ForeignKey(Visitor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    approved = models.BooleanField()
    reviewed = models.BooleanField()
    name_displayed = models.BooleanField()
    comment = models.TextField()

    def __str__(self):
        return "Commentaire de %s (%s/%s) - %s" % (
            self.user,
            "validé" if self.approved else "non validé",
            "nom affiché" if self.name_displayed else "anonyme",
            (self.comment[:25] + '...') if len(self.comment) > 25 else self.comment,
        )

QUESTIONS_TYPES = (
    ("YES_NO", "Oui/non"),
    ("TEXTAREA", "Champ libre"),
    ("RATING_STARS", "Évaluation - 5 étoiles"),
    ("RATING_10_5_0", "Évaluation - 10/5/0"),
)

class CityProjectQuestion(BaseModel):
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE)
    question_statement = models.CharField(max_length=200)
    type = models.CharField(max_length=50,
                      choices=QUESTIONS_TYPES,
                      default="TEXTAREA")
    ratings_10_5_0_values = ["Plus de 10 fois", "Entre 5 et 10 fois",
        "Moins de 5 fois", "Jamais"]
    yes_no = ["Oui", "Non"]
    def __str__(self):
        return "Question (%s) sur le projet %s: %s" % (
            self.type,
            self.project,
            self.question_statement,
        )

class CityProjectAnswer(BaseModel):
    question = models.ForeignKey(CityProjectQuestion, on_delete=models.CASCADE)
    visitor = models.ForeignKey(Visitor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    text_answer = models.TextField()
    numeric_answer = models.IntegerField(default=0)

    def __str__(self):
        question_short = str(self.question)[:40] + (str(self.question)[40:] and '...')
        answer_short = ""
        if self.question.type == "YES_NO":
            answer_short = CityProjectQuestion.yes_no[self.numeric_answer]
        elif self.question.type == "TEXTAREA":
            answer_short = str(self.text_answer)[:40] + (str(self.text_answer)[40:] and '...')
        elif self.question.type == "RATING_STARS":
            answer_short = "1 étoile" if self.numeric_answer == 0 else "%d étoiles " % self.numeric_answer
        elif self.question.type == "RATING_10_5_0":
            answer_short = CityProjectQuestion.ratings_10_5_0_values[self.numeric_answer]

        user_short_form = "un utilisateur anonyme"
        if self.user != None:
            user_short_form = self.user.username


        return "Réponse à la question \"%s\" = %s (par %s)" % (
            question_short,
            answer_short,
            user_short_form
        )



class Proposition(BaseModel):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" % (self.title,
            "Approuvée" if self.approved else "Non approuvée"
        )

    def save(self, *args, **kwargs):
        """
        Quickly overriding the super()-function in order to also save a
        thumbnail.
        """
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            createThumbnail(self.image.path)




class PropositionSignature(BaseModel):
    proposition = models.ForeignKey(Proposition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s " % (str(self.user), self.proposition.title)

class PropositionComment(BaseModel):
    proposition = models.ForeignKey(Proposition, on_delete=models.CASCADE)
    visitor = models.ForeignKey(Visitor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    approved = models.BooleanField()
    reviewed = models.BooleanField()
    name_displayed = models.BooleanField()
    comment = models.TextField()

    def __str__(self):
        return "Commentaire de %s (%s/%s) - %s" % (
            self.user,
            "validé" if self.approved else "non validé",
            "nom affiché" if self.name_displayed else "anonyme",
            (self.comment[:25] + '...') if len(self.comment) > 25 else self.comment,
        )

# Logging the approvals:
class PropositionCommentReview(BaseModel):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    comment = models.ForeignKey(PropositionComment, on_delete=models.CASCADE)
    review_decision = models.BooleanField() # local copy of the value for log purposes

class CityProjectCommentReview(BaseModel):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    comment = models.ForeignKey(CityProjectComment, on_delete=models.CASCADE)
    review_decision = models.BooleanField() # local copy of the value for log purposes
class PropositionReview(BaseModel):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
        null=True)
    proposition = models.ForeignKey(Proposition, on_delete=models.CASCADE)
    review_decision = models.BooleanField() # local copy of the value for log purposes
