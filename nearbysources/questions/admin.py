from nearbysources.questions.models import *
from django.contrib import admin

admin.site.register(Language)
admin.site.register(Campaign)
admin.site.register(LocationOfInterest)

class QuestionnaireTweetI(admin.TabularInline):
    model = QuestionnaireTweet

class QuestionnaireTitleI(admin.TabularInline):
    model = QuestionnaireTitle

class QuestionnaireIntroI(admin.TabularInline):
    model = QuestionnaireIntro

class QuestionnaireMoreInfoI(admin.TabularInline):
    model = QuestionnaireMoreInfo

class QuestionnaireThankYouI(admin.TabularInline):
    model = QuestionnaireThankYou

class QuestionI(admin.TabularInline):
    model = Question

class QuestionnaireMA(admin.ModelAdmin):
    inlines = [QuestionnaireTweetI, QuestionnaireTitleI, QuestionnaireIntroI, QuestionnaireMoreInfoI, QuestionnaireThankYouI, QuestionI]

admin.site.register(Questionnaire, QuestionnaireMA)
admin.site.register(QuestionnaireTitle)
admin.site.register(QuestionnaireIntro)
admin.site.register(QuestionnaireMoreInfo)
admin.site.register(QuestionnaireTweet)
admin.site.register(QuestionnaireThankYou)

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
admin.site.register(TwitterRequest)
