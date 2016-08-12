from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView

from find_roommate.forms import HousingInfoUpdateForm, HousingSearchForm
from find_roommate.models import HousingUser
from undergraduate_admission.validators import is_eligible_for_housing, is_eligible_for_roommate_search


@login_required()
@user_passes_test(is_eligible_for_housing)
def housing_info_update(request):
    housing_user, d = HousingUser.objects.get_or_create(user=request.user,defaults={'searchable': False,})
    form = HousingInfoUpdateForm(request.POST or None,
                                 instance=housing_user)

    if request.method == 'POST':

        if form.is_valid():
            saved = form.save()
            if saved:
                if saved.searchable:
                    return redirect('housing_search')
                else:
                    return redirect('student_area')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'find_roommate/housing_update_form.html', {'form': form,})


@login_required()
@user_passes_test(is_eligible_for_roommate_search)
def housing_search(request):
    if request.GET:
        form = HousingSearchForm(request.GET)
        if form.is_valid():
            students = HousingUser.objects\
                .filter(user__status_message__status_message_code='ADMITTED')

            try:
                high_school_city = request.GET['high_school_city']
                if high_school_city:
                    students = students.filter(
                        user__high_school_city__contains=high_school_city)

                high_school_name = request.GET['high_school_name']
                if high_school_name:
                    students = students.filter(
                        user__high_school_name__contains=high_school_name)

                light = request.GET['light']
                if light:
                    students = students.filter(light=light)

                room_temperature = request.GET['room_temperature']
                if room_temperature:
                    students = students.filter(room_temperature=room_temperature)

                visits = request.GET['visits']
                if visits:
                    students = students.filter(visits=visits)

                sleeping = request.GET['sleeping']
                if sleeping:
                    students = students.filter(sleeping=sleeping)

            except MultiValueDictKeyError:
                pass

        else:
            students = HousingUser.objects.all()
    else:
        form = HousingSearchForm()
        students = HousingUser.objects.all()

    paginator = Paginator(students, 10)

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    return render(request, 'find_roommate/housinguser_list.html', {'page_obj': objects,
                                                                   'form': form,})


class PostList(ListView):
    paginate_by = 1

    def get_queryset(self):
        if 'search' in self.request.GET:
            objects = HousingUser.objects.all()
        else:
            objects = HousingUser.objects.all()
        return objects