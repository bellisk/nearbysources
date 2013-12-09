from nearbysources.questions.models import *
from django.shortcuts import render_to_response, redirect
from django.shortcuts import get_object_or_404 as go4
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json, csv, StringIO
from django.http import HttpResponse

def frontpage(request):
    c = {}
    c["questionnaires"] = Questionnaire.objects.all()
    return render_to_response("frontpage.html", c)

def questionnaire(request, q_id, l_id, language):
    c = {}
    lang = go4(Language, code=language)
    q = go4(Questionnaire, id=q_id)
    l = go4(LocationOfInterest, id=l_id)
    c["q_id"] = q.id
    c["l_id"] = l.id
    c["title"] = go4(QuestionnaireTitle, questionnaire=q, language=lang).text.replace("{{location}}", l.name)
    c["intro"] = go4(QuestionnaireIntro, questionnaire=q, language=lang).text.replace("{{location}}", l.name)
    c["questions"] = [{"id": question.id, "text": go4(QuestionText, question=question, language=lang).text, "options": [{"id": option.id, "text": go4(OptionText, option=option, language=lang).text} for option in question.options.all()]} for question in q.questions.all()]
    c["language"] = language
    return render_to_response("questionnaire.html", c)

@csrf_exempt
def submit_response(request, q_id, l_id, language):
    response = {"success": False}
    if request.method == "POST":
        r = Response(questionnaire=go4(Questionnaire, id=q_id), location=go4(LocationOfInterest, id=l_id))
        r.save()
        data = json.loads(request.POST["data"])
        for answer in data["answers"]:
            Answer(response=r, question=go4(Question, id=answer["question"]), option=go4(Option, id=answer["option"])).save()
        response["success"] = True
        response["redirect"] = reverse("nearbysources.questions.views.thankyou", args=[q_id, l_id, language])
    return HttpResponse(json.dumps(response))

def thankyou(request, q_id, l_id, language):
    return render_to_response("thankyou.html", {"thankyou": go4(QuestionnaireThankYou, questionnaire=go4(Questionnaire, id=q_id), language=go4(Language, code=language)).text})

def info(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    c = {}
    c["q_id"] = q_id
    c["language"] = language
    c["title"] = go4(QuestionnaireTitle, questionnaire=q, language=lang).text.replace("{{location}}", "[?]")
    c["more_info"] = go4(QuestionnaireMoreInfo, questionnaire=q, language=lang).text.replace("{{location}}", "[?]")
    return render_to_response("info.html", c)
    
def search(request, q_id, language):
    c = {}
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    c["q_id"] = q_id
    c["title"] = go4(QuestionnaireTitle, questionnaire=q, language=lang).text
    c["language"] = language
    if "query" in request.GET:
        c["query"] = request.GET["query"]
        c["results"] = LocationOfInterest.objects.filter(campaign=q.campaign, name__icontains=request.GET["query"])
    else:
        c["results"] = LocationOfInterest.objects.all()
    return render_to_response("search.html", c)

def grey_if_zero(n):
    if n == 0:
        return '<span style="color:grey;">' + str(n) + '</span>'
    else:
        return str(n)

def results(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    c = {}
    c["name"] = q.name
    c["headers"] = [
        [["", True, 1], ["", True, 1]] + [[go4(QuestionText, question=question, language=lang).text, True, len(question.options.all())] for question in q.questions.order_by("name").all()],
        [["Location", True, 1], ["Responses", True, 1]] + [[go4(OptionText, option=option, language=lang).text + ", %", option.id == question.options.order_by("name").all()[0].id, 1] for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()]
    ]
    c["data"] = [[(loc.name, True), (len(loc.responses.all()), True)] + [(grey_if_zero(len(Answer.objects.filter(response__location=loc, option=option)) * 100 // len(Answer.objects.filter(response__location=loc, question=question))), option.id == question.options.order_by("name").all()[0].id) for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()] for loc in q.campaign.locations.order_by("name").all() if len(loc.responses.all()) > 0]
    return render_to_response("results.html", c)

def csvresults(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    output = StringIO.StringIO()
    csv_writer = csv.writer(output)
    csv_header1 = [u"", u""]
    [csv_header1.extend([go4(QuestionText, question=question, language=lang).text, "" * (len(question.options.all()) - 1)]) for question in q.questions.order_by("name").all()]
    csv_writer.writerow(csv_header1)
    csv_header2 = [u"Location", u"Responses"]
    csv_header2.extend([go4(OptionText, option=option, language=lang).text + ", %" for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()])
    csv_writer.writerow(csv_header2)
    for loc in [loc for loc in q.campaign.locations.order_by("name").all() if len(loc.responses.all()) > 0]:
        csv_line = [loc.name, str(len(loc.responses.all()))]
        for question in q.questions.order_by("name").all():
            for option in [option for option in question.options.order_by("name").all()]:
                csv_line.extend([str(len(Answer.objects.filter(response__location=loc, option=option)) * 100 // len(Answer.objects.filter(response__location=loc, question=question)))])
        csv_writer.writerow(csv_line)
    print output.getvalue()
    return HttpResponse(output.getvalue(), content_type='text/csv')
