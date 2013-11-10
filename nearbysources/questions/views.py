from nearbysources.questions.models import *
from django.shortcuts import render_to_response, redirect
from django.shortcuts import get_object_or_404 as go4
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse

def frontpage(request):
    return render_to_response("frontpage.html")

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

def results(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    c = {}
    c["name"] = q.name
    c["headers"] = [
        [["", 1], ["", 1]] + [[go4(QuestionText, question=question, language=lang).text, len(question.options.all())] for question in q.questions.order_by("name").all()],
        [["Location", 1], ["Responses", 1]] + [[go4(OptionText, option=option, language=lang).text, 1] for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()]
    ]
    c["data"] = [[loc.name, len(loc.responses.all())] + [str(len(Answer.objects.filter(response__location=loc, option=option)) * 100 / len(Answer.objects.filter(response__location=loc, question=question))) + "%" for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()] for loc in q.campaign.locations.order_by("name").all() if len(loc.responses.all()) > 0]
    return render_to_response("results.html", c)
    #return HttpResponse(json.dumps(c, indent=4))
