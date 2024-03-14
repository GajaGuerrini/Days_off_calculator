from django.db import models

# Create your models here.
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=10)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=2)
    votes = models.IntegerField(default=0)