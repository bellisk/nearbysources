from nearbysources.questions.models import *
from django.contrib import admin

admin.site.register(Language)
admin.site.register(Campaign)
admin.site.register(LocationOfInterest)

class QuestionnaireIntroI(admin.TabularInline):
    model = QuestionnaireIntro

class QuestionI(admin.TabularInline):
    model = Question

class QuestionnaireMA(admin.ModelAdmin):
    inlines = [QuestionnaireIntroI, QuestionI]

admin.site.register(Questionnaire, QuestionnaireMA)
admin.site.register(QuestionnaireIntro)

class QuestionTextI(admin.TabularInline):
    model = QuestionText

class OptionI(admin.TabularInline):
    model = Option

class QuestionMA(admin.ModelAdmin):
    inlines = [QuestionTextI, OptionI]

admin.site.register(Question, QuestionMA)
admin.site.register(QuestionText)

class OptionTextI(admin.TabularInline):
    model = OptionText

class OptionMA(admin.ModelAdmin):
    inlines = [OptionTextI]

admin.site.register(Option, OptionMA)
admin.site.register(OptionText)

class AnswerI(admin.TabularInline):
    model = Answer

class ResponseMA(admin.ModelAdmin):
    inlines = [AnswerI]

admin.site.register(Response, ResponseMA)
admin.site.register(Answer)
