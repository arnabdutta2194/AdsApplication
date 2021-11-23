from re import template
import re
from django.db import models
from ads.models import Ad, Comment, Fav
from ads.forms import CreateForm
from ads.forms import CommentForm
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile


class AdListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "ads/ad_list.html"

    def get(self,request):
        ad_list = Ad.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [row['id'] for row in rows]
        ctx = {'ad_list' : ad_list, 'favorites':favorites}
        return render(request,self.template_name,ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"
    def get(self, request, pk) :
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

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

class CommentCreateView(LoginRequiredMixin,View):
    def post(self,request,pk):
        a = get_object_or_404(Ad,id=pk)
        comment=Comment(text=request.POST['comment'],owner =request.user, ad=a)
        comment.save()
        return redirect(reverse('ads:ad_detail',args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model=Comment
    template_name = "ads/comment_delete.html"
    
    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id]) #To go back to forum


#Runs when we do a view image on any picture
def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type #get from model
    response['Content-Length'] = len(pic.picture) #get from model
    response.write(pic.picture) #display on ui
    return response

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()