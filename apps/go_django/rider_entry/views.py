import datetime

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Metadata, Data, Driver, Stop, Vehicle


class IndexView(generic.ListView):
    template_name = 'rider_entry/index.html'
    context_object_name = 'latest_metadata_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Metadata.objects.filter(date__lte=datetime.date.today()).order_by('-date')[:5]


class DetailView(generic.DetailView):
    model = Metadata
    template_name = 'rider_entry/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Metadata.objects.filter(date__lte=datetime.date.today())


"""
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
"""