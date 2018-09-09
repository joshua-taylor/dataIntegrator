from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse
    from django.utils.functional import lazy
    reverse_lazy = lambda *args, **kwargs: lazy(reverse, str)(*args, **kwargs)
from django.views import generic

from uploads.core.models import Document, CustomUser
from mapping.models import Requests, Template
from uploads.core.forms import DocumentForm, CustomUserCreationForm
from django.shortcuts import get_object_or_404






@login_required(login_url='/login/')
def delete(request):
    # if request.method != 'POST':
    #     raise HTTP404

    docId = request.POST.get('docfile', None)
    docToDel = get_object_or_404(Document, pk = docId)
    #_delete_file(docToDel.document.name)
    docToDel.delete()

    return HttpResponseRedirect(reverse('dashboard'))



@login_required(login_url='/login/')
def dashboard(request):
    username = None
    if request.user.is_authenticated():
        email = request.user.email #used in the responses filter below
    documents = Document.objects.filter(owner=request.user).all()
    requests = Requests.objects.filter(creator=request.user).all()
    responses = Requests.objects.filter(send_to__icontains=str(email),status__icontains=str("ACTIVE"))
    return render(request, 'core/dashboard.html', { 'documents': documents ,'name' : request.user.username, 'requests': requests, 'responses': responses })


@login_required(login_url='/login/')
def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST,  request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner =  request.user
            post.save()
            return redirect('dashboard')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    })

def home(request):
    return render(request, 'core/home.html')

def logged_out(request):
    return render(request, 'core/logout.html')

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = './registration/signup.html'
