from django.db import models

# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6)
    def __unicode__(self):
        return self.name

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    questionnaire = models.OneToOneField("Questionnaire", related_name="+")
    def __unicode__(self):
        return self.name

class LocationOfInterest(models.Model):
    campaign = models.ForeignKey("Campaign", related_name="locationsOfInterest")
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    class Meta:
        verbose_name_plural = "LocationsOfInterest"
    def __unicode__(self):
        return self.name

class Questionnaire(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

class QuestionnaireIntro(models.Model):
    questionnaire = models.ForeignKey("Questionnaire", related_name="intros")
    language = models.ForeignKey("Language", related_name="+")
    text = models.TextField()
    def __unicode__(self):
        return self.text[:80]

class Question(models.Model):
    questionnaire = models.ForeignKey("Questionnaire", related_name="questions")
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

class QuestionText(models.Model):
    question = models.ForeignKey("Question", related_name="texts")
    language = models.ForeignKey("Language", related_name="+")
    text = models.TextField()
    def __unicode__(self):
        return self.text[:80]

class Option(models.Model):
    question = models.ForeignKey("Question", related_name="options")
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

class OptionText(models.Model):
    option = models.ForeignKey("Option", related_name="texts")
    language = models.ForeignKey("Language", related_name="+")
    text = models.TextField()
    def __unicode__(self):
        return self.text[:80]

class Response(models.Model):
    questionnaire = models.ForeignKey("Questionnaire", related_name="responses")
    datetime = models.DateTimeField(auto_now_add=True)
    def summary(self):
        return ", ".join(a.summary() for a in self.answers)
    def __unicode__(self):
        return self.summary()[:80]

class Answer(models.Model):
    response = models.ForeignKey("Response", related_name="answers")
    question = models.ForeignKey("Question", related_name="answers")
    option = models.ForeignKey("Option", related_name="answers")
    def summary(self):
        return str(self.question) + ": " + str(self.option)
    def __unicode__(self):
        return self.summary()[:80]
