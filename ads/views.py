from ads.models import Ad
from ads.forms import CreateForm
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.files.uploadedfile import InMemoryUploadedFile


class AdListView(OwnerListView):
    model = Ad
    # By convention:
    # template_name = "ads/ad_list.html"


class AdDetailView(OwnerDetailView):
    model = Ad


class AdCreateView(LoginRequiredMixin,View):
    # model = Ad
    # fields = ['title', 'price', 'text'] #Which fields are to be shown on the screen
    template_name = "ads/ad_form.html"
    success_url = reverse_lazy('ads:all')

    def get(self,request,pk=None):
        form = CreateForm()
        ctx = {'form':form}
        return render(request, self.template_name,ctx)

    def post(self,request,pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form':form}
            return render(request,self.template_name,ctx)
        
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        return redirect(self.success_url)

class AdUpdateView(LoginRequiredMixin,View):
    # model = Ad
    # fields = ['title', 'price' ,'text']

    template_name = "ads/ad_form.html"
    success_url = reverse_lazy('ads:all')

    def get(self,request,pk):
        ad = get_object_or_404(Ad,id=pk,owner = self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form':form}
        return render(request, self.template_name,ctx)

    def post(self,request,pk=None):
        ad = get_object_or_404(Ad,id=pk,owner = self.request.user)
        form = CreateForm(request.POST, request.FILES or None,instance=ad)

        if not form.is_valid():
            ctx = {'form':form}
            return render(request,self.template_name,ctx)
        
        ad = form.save(commit=False)
        ad.save()
        
        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad

#Runs when we do a view image on any picture
def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type #get from model
    response['Content-Length'] = len(pic.picture) #get from model
    response.write(pic.picture) #display on ui
    return response