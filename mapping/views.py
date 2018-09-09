from django.shortcuts import render, redirect
from django.core.files import File
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import pandas as pd
pd.set_option('max_colwidth', 100)
import os
import uploads.settings as settings
from mapping.models import Requests, Template, Response, ResponseFile
from uploads.core.models import Document, CustomUser
from mapping.email import *

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.utils.functional import lazy
    reverse_lazy = lambda *args, **kwargs: lazy(reverse, str)(*args, **kwargs)
from .forms import TemplateForm, RequestForm, MappingForm
from django.shortcuts import get_object_or_404




@login_required(login_url='/login/')
def map(request, req_id):
    req = Requests.objects.get(pk=req_id)
    documents = Document.objects.filter(owner=request.user).all()
    return render(request, "map.html", { 'documents': documents ,'req' : req, 'req_id':req_id})

#FILE SUMMARY & MAPPING HERE:
#includes choosing a file, showing summary metrics, mapping to request
@login_required(login_url='/login/')
def map2(request, req_id, doc_id, file_accept):
    if request.method == 'GET':
        #This gets the information required for the workflow and also presents a preview of an uploaded file prior to mapping:
        documents = Document.objects.get(pk=doc_id)
        request_info = Requests.objects.get(pk=req_id)
        template = Template.objects.filter(Request_id=req_id)
        responses = Response.objects.filter(Request_id=req_id,creator=request.user)
        if documents.document.name.split('.')[-1] == 'csv':  #if a csv file:
            df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,documents.document.name), parse_dates=True)
        elif documents.document.name.split('.')[-1] in 'xlsx': #if the end of a file is in xlsx (to include xls files as well)
            df = pd.read_excel(os.path.join(settings.MEDIA_ROOT,documents.document.name))
        else:
            raise Http404("Oh no! It looks like we could not read in the file. Please double check that the file ends in either '.xlxs' or '.csv'.")
        df_html = df.head().to_html(classes=["table table-hover-striped","table-borderless", "table-striped", "table-hover"],index=False,bold_rows=True)
        describe = df.describe().to_html(classes=["table table-hover-striped", "table-striped", "table-hover"],index=True,bold_rows=True)
        rows = df.shape[0]
        columns = df.shape[1]
        col_names = df.columns
        formset = MappingForm()

     ### creation of mapped file
        if file_accept == '2':
            mapped_names = responses.values_list('field_name') # these are the names from the origional request template
            origional_names = responses.values_list('mapped_field_name') # these are the names from a response file
            dtypes = responses.values_list('type')
            manditory = responses.values_list('manditory')
            max_len = responses.values_list('max_len')
            df['Issue(s) Noted'] = 0
            df['Issue Detail'] = ''
            for i, field in enumerate(mapped_names):
                if origional_names[i][0] == 'No match':
                    df[field[0]] = float('nan')
                else:
                    df[field[0]] = df[origional_names[i][0]]
                if manditory[i][0] == 'True':
                    df['Issue Detail'].loc[df[field[0]].isnull()] = df['Issue Detail'] + 'Issue noted at ' + str(field[0]) + ': manditory field is blank.|'
                    df['Issue(s) Noted'].loc[df[field[0]].isnull()] = df['Issue(s) Noted'].loc[df[field[0]].isnull()] +1
                if dtypes[i][0] == 'Text':
                    try:
                        df['Issue Detail'].loc[df[field[0]].str.len()>max_len[i][0]] = df['Issue Detail'] + 'Issue noted at ' + str(field[0]) + ': field exceeds maximum length specified.|'
                        df['Issue(s) Noted'].loc[df[field[0]].str.len()>max_len[i][0]] = df['Issue(s) Noted'].loc[df[field[0]].str.len()>max_len[i][0]] + 1
                    except:
                        pass
                if dtypes[i][0] == 'Number':
                    df[field[0]] = pd.to_numeric(df[field[0]], errors='coerce')
                    df['Issue Detail'].loc[df[field[0]].isnull()] = df['Issue Detail'] + 'Issue noted at ' + str(field[0]) + ': non numeric type detected.|'
                    df['Issue(s) Noted'].loc[df[field[0]].isnull()] = df['Issue(s) Noted'].loc[df[field[0]].isnull()] + 1
                elif dtypes[i][0] == 'Date':
                    df[field[0]] = pd.to_datetime(df[field[0]],errors='coerce',dayfirst=True,exact=False, infer_datetime_format=True)
                    df['Issue Detail'].loc[df[field[0]].isnull()] = df['Issue Detail'] + 'issue noted at ' + str(field[0]) + ': could not convert to date format|'
                    df['Issue(s) Noted'].loc[df[field[0]].isnull()] = df['Issue(s) Noted'].loc[df[field[0]].isnull()] + 1
            fieldlist = [x[0] for x in mapped_names] + ['Issue(s) Noted','Issue Detail']
            df = df[fieldlist]
            df_html = df.to_html(classes=["table table-hover-striped","table-borderless", "table-striped", "table-hover"],index=False,bold_rows=True)
            df['Created by'] = str(request.user)
            #saving the actual file as pickle:
            path = 'media/mappedFiles/'+str(req_id)+'_'+str(doc_id)+'.pkl'
            df.to_pickle(path)
            #delete older submissions:
            object = ResponseFile.objects.filter(Request_id=req_id,creator=request.user)
            object.delete()
            #creating a corresponding entry in the DB to add meta data and track the path of the file:
            savePickle = ResponseFile()
            savePickle.Request_id = req_id
            savePickle.creator = request.user
            savePickle.rows = df.shape[0]
            savePickle.badRows = df['Issue(s) Noted'].astype(bool).sum(axis=0)
            savePickle.type = "RESPONSE"
            savePickle.documentPath = path
            savePickle.save() # first save the meta data for the file - then use FileField to save the file into the model (below):
            local_file = open(path,  'rb') #for saving into filefield
            savePickle =  ResponseFile.objects.get(pk=savePickle.id)
            savePickle.document.save('path', File(local_file))

            #for handling posts - one for deleting a response template - the other for submitting a finished template:
    elif request.method == 'POST':
        post_data = {}
        for key, values in request.POST.lists():
            post_data[key] = values
        if post_data.get('delete'):
            responses = Response.objects.filter(Request_id=req_id,creator=request.user)
            responses.delete()
            return redirect('map2', req_id=req_id, doc_id=doc_id, file_accept=1 )
        for i in range(len(post_data['mapped_field_name'])):
            formset = MappingForm()
            post = formset.save(commit=False)
            post.mapped_field_name = post_data['mapped_field_name'][i]
            post.field_name = post_data['field_name'][i]
            post.type = post_data['type'][i]
            post.desc = post_data['desc'][i]
            post.max_len = post_data['max_len'][i]
            post.manditory = post_data['manditory'][i]
            post.Request_id = req_id
            post.creator = request.user
            post.status = 'DRAFT'
            post.save()
        return redirect('map2', req_id=req_id, doc_id=doc_id, file_accept=file_accept )
    return render(request, "map2.html", { 'documents': documents ,'name' : request.user.username, 'df_html' :df_html,
    'describe' : describe, 'rows':rows, 'columns':columns, 'doc_id':doc_id, 'req_id':req_id, 'file_accept':file_accept,
    'template':template, 'col_names':col_names, 'formset':formset, 'responses':responses, 'req':request_info  })



#CREATE REQUEST
@login_required(login_url='/login/')
def create_request_form(request):
    template_name = 'requests.html'
    if request.method == 'GET':
        form = RequestForm()
    elif request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator =  request.user
            post.save()
            return redirect(str(post.id)+'/template',requests_id = post.id)
    return render(request, template_name, {
        'form': form,
    })


#UPDATE REQUEST
@login_required(login_url='/login/')
def update_request_form(request, pk):
    template_name = 'requests.html'
    req = Requests.objects.get(id=pk)
    form = RequestForm(request.POST or None, instance = req)
    if form.is_valid():
        form.save()
        return redirect(str(pk)+'/template',requests_id = pk)
    return render(request, template_name, {
        'form': form,
        'mapping': req,
    })



# TEMPLATE:
@login_required(login_url='/login/')
def create_template_form(request, requests_id):
    template_name   = 'template.html'
    heading_message = 'Request template'
    req_header      = Requests.objects.get(pk=requests_id)
    template        = Template.objects.filter(Request_id=requests_id)
    responses       = ResponseFile.objects.filter(Request_id=requests_id,type__icontains="RESPONSE")
    downloads       = ResponseFile.objects.filter(Request_id=requests_id,type__icontains="DOWNLOAD")
    if request.method == 'GET':
        formset     = TemplateForm()
    elif request.method == 'POST':
        formset     = TemplateForm(request.POST)
        if formset.is_valid():
            post    = formset.save(commit=False)
            post.Request_id = requests_id
            post.save()
            return redirect(request.path_info)
    return render(request, template_name, {
        'formset': formset,
        'req_header': req_header,
        'template': template,
        'heading': heading_message,
        'responses' : responses,
        'downloads' : downloads
    })

# TEMPLATE changestatus of a draft request template (button form from template.html):
@login_required(login_url='/login/')
def reqstatus(request):
    if request.method   == 'POST':
        object          =   Requests.objects.get(id=int(request.POST.get('reqID')))
        object.status   =   request.POST.get('status')
        if request.POST.get('status') == 'ACTIVE':
            recipient = object.send_to.split(',')
            sender = object.creator
            title  = object.name
            desc   = object.desc
            sendEmail(recipient,sender,title,desc)
        object.save()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


# TEMPLATE creates a file for download from responses recieved:
@login_required(login_url='/login/')
def requestDownload(request):
    if request.method   == 'POST':
        post_data = {}
        for key, values in request.POST.lists():
            post_data[key] = values
        df = pd.DataFrame()
        if post_data.get('file'):
            for i in post_data.get('file'):
                fileRequest = ResponseFile.objects.get(pk=int(i),type__icontains="RESPONSE")
                if fileRequest: #need an if statement here as will have a file which is a download file potentilly so will not be found by the query above
                    dftemp = pd.read_pickle(fileRequest.documentPath)
                    df = pd.concat([df,dftemp])
            path = 'media/tmp/'+str(post_data.get('req_id')[0])+'.csv'
            df.to_csv(path)
            #delete older submissions:
            object = ResponseFile.objects.filter(Request_id=int(post_data.get('req_id')[0]),type__icontains="DOWNLOAD")
            object.delete()
            #creating a corresponding entry in the DB to add meta data and track the path of the file:
            saveCSV = ResponseFile()
            saveCSV.Request_id = int(post_data.get('req_id')[0])
            saveCSV.creator = request.user
            saveCSV.rows = df.shape[0]
            saveCSV.badRows = df['Issue(s) Noted'].sum()
            saveCSV.documentPath = path
            saveCSV.type = "DOWNLOAD"
            saveCSV.save() # first save the meta data for the file - then use FileField to save the file into the model (below):
            local_file = open(path,  'r') #for saving into filefield
            saveCSV =  ResponseFile.objects.get(pk=saveCSV.id)
            saveCSV.document.save('path', File(local_file))
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

#FOR deleting template items:
@login_required(login_url='/login/')
def delete_template(request, pk =None):
    if request.method == 'POST':
        object = Template.objects.get(id=pk)
        object.delete()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

#For deleting requests:
@login_required(login_url='/login/')
def delete_requests(request, pk =None):
    if request.method == 'POST':
        object = Requests.objects.get(id=pk)
        object.delete()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
