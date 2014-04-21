from nearbysources.questions.models import *
from django.shortcuts import render_to_response, redirect
from django.shortcuts import get_object_or_404 as go4
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json, csv, StringIO, math
from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring

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
    csv_header1 = [u"", u"", u"", u""]
    for question in q.questions.order_by("name").all():
        csv_header1.extend([go4(QuestionText, question=question, language=lang).text] + [""] * (len(question.options.all()) - 1)) 
    csv_writer.writerow(csv_header1)
    csv_header2 = [u"Location", u"Latitude", u"Longitude", u"Responses"]
    csv_header2.extend([go4(OptionText, option=option, language=lang).text + ", %" for question in q.questions.order_by("name").all() for option in question.options.order_by("name").all()])
    csv_writer.writerow(csv_header2)
    for loc in [loc for loc in q.campaign.locations.order_by("name").all() if len(loc.responses.all()) > 0]:
        csv_line = [loc.name, loc.lng, loc.lat, str(len(loc.responses.all()))]
        for question in q.questions.order_by("name").all():
            for option in [option for option in question.options.order_by("name").all()]:
                csv_line.extend([str(len(Answer.objects.filter(response__location=loc, option=option)) * 100 // len(Answer.objects.filter(response__location=loc, question=question)))])
        csv_writer.writerow(csv_line)
    return HttpResponse(output.getvalue(), content_type='text/csv')

def jsonresults(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    results_dict = {"Questionnaire": q.name, "Language": lang.name, "Locations": []}
    for loc in [loc for loc in q.campaign.locations.all() if len(loc.responses.all()) > 0]:
        questions_dict = {}
        for question in q.questions.all():
            questions_dict[go4(QuestionText, question=question, language=lang).text] = {}
            for option in question.options.all():
                questions_dict[go4(QuestionText, question=question, language=lang).text][go4(OptionText, option=option, language=lang).text] = len(Answer.objects.filter(response__location=loc, option=option))
        location_dict = {"Name": loc.name, "Longitude": loc.lng, "Latitude": loc.lat, "No. of responses": len(loc.responses.all()), "Questions": questions_dict}
        results_dict["Locations"].append(location_dict)
    return HttpResponse(json.dumps(results_dict), content_type='application/json')

def kmlresults(request, q_id, language):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    kml = Element("kml")
    kml.set("xmlns", "http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, "Document")
    doc_name = SubElement(doc, "name")
    doc_name.text = go4(QuestionnaireTitle, questionnaire=q, language=lang).text
    style = SubElement(doc, "Style")
    style.set("id", "nbs_style")
    bstyle = SubElement(style, "BalloonStyle")
    bstyle_text = SubElement(bstyle, "text")
    t = ""
    for question in q.questions.order_by("name").all():
        t += '<div class="question"><div class="question_text" style="font-weight: bold;">'
        t += go4(QuestionText, question=question, language=lang).text
        t += '</div><table>'
        for option in [option for option in question.options.order_by("name").all()]:
            t += '<tr><td>'
            t += go4(OptionText, option=option, language=lang).text
            t += '</td><td>$['
            t += str(option.id)
            t += ']%</td></tr>'
        t += '</table></div>'
    bstyle_text.text = t
    for loc in [loc for loc in q.campaign.locations.all() if len(loc.responses.all()) > 0]:
        pm = SubElement(doc, "Placemark")
        styleUrl = SubElement(pm, "styleUrl")
        styleUrl.text = "#nbs_style"
        name = SubElement(pm, "name")
        name.text = loc.name
        pt = SubElement(pm, "Point")
        coords = SubElement(pt, "coordinates")
        coords.text = str(loc.lng) + "," + str(loc.lat) + ",0"
        ed = SubElement(pm, "ExtendedData")
        for question in q.questions.order_by("name").all():
            for option in [option for option in question.options.order_by("name").all()]:
                percentage = str(len(Answer.objects.filter(response__location=loc, option=option)) * 100 // len(Answer.objects.filter(response__location=loc, question=question)))
                data = SubElement(ed, "Data")
                data.set("name", str(option.id))
                display_name = SubElement(data, "displayName")
                display_name.text = go4(QuestionText, question=question, language=lang).text + " " + go4(OptionText, option=option, language=lang).text
                value = SubElement(data, "value")
                value.text = percentage
    return HttpResponse(tostring(kml), content_type="application/vnd.google-earth.kml+xml")

def get_all_questions_and_locations(request, q_id, language, page):
    q = go4(Questionnaire, id=q_id)
    lang = go4(Language, code=language)
    results_dict = {"Questionnaire": q.name, "Language": lang.name, "Questions": [], "Locations": [], "Pages": 0}

    # Constructing a dictionary with all questions and options in it
    questions_dict = {}
    for question in q.questions.all():
        question_dict = {"ID": question.id, "Text": go4(QuestionText, question=question, language=lang).text, "Options": []}
        for option in question.options.all():
            option_dict = {"ID": option.id, "Text": go4(OptionText, option=option, language=lang).text}
            question_dict["Options"].append(option_dict)
        results_dict["Questions"].append(question_dict)

    # Pagination: 100 locations at a time
    start_id = (page - 1) * 100 + 1
    end_id = page * 100
    results_dict["Pages"] = math.ceil(len(q.campaign.locations.all()) * page / 100)

    # Constructing a list of all locations, with name + id + lat/lng + results
    for loc in q.campaign.locations.filter(id__range=(start_id, end_id)):
        questions_dict = {}
        for question in q.questions.all():
            questions_dict[question.id] = {}
            for option in question.options.all():
                questions_dict[question.id][option.id] = len(Answer.objects.filter(response__location=loc, option=option))
        location_dict = {"ID": loc.id, "Name": loc.name, "Longitude": loc.lng, "Latitude": loc.lat, "Questions": questions_dict}
        results_dict["Locations"].append(location_dict)

    return HttpResponse(json.dumps(results_dict), content_type='application/json')
