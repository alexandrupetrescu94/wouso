from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.user.models import UserProfile
from wouso.interface.messaging.models import Message, MessagingUser
from wouso.interface.messaging.forms import ComposeForm


@login_required
def home(request, quiet=None, box=None, page=u'0'):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    if box == 'rec' or box is None:
        messages = Message.objects.filter(receiver=msg_user)
    elif box == 'sent':
        messages = Message.objects.filter(sender=msg_user)
    elif box == 'all':
        messages = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))

    if quiet is not None:
        template = 'messaging/message.html'
    else:
        template = 'messaging/index.html'

    return render_to_response(template,
                              {'user': request.user,
                               'messages': messages
                               },
                              context_instance=RequestInstance(request))


@login_required
def create(request, to=None):
    if to is not None:
        to = get_object_or_404(UserProfile, pk=to)

    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            m = Message.send(request.user.get_profile(),
                            form.cleaned_data['to'],
                            form.cleaned_data['subject'],
                            form.cleaned_data['text']
            )
            return HttpResponseRedirect(reverse('wouso.interface.messaging.views.home'))
        #else:
        #   print form, form.is_valid(), request.POST
    return render_to_response('messaging/create.html',
                              {'to': to},
                              context_instance=RequestContext(request))

@login_required
def message(request, mid):
    message = get_object_or_404(Message, pk=mid)

    me = request.user.get_profile().get_extension(MessagingUser)

    if message.sender == me or message.receiver == me:
        return render_to_response('messaging/message_one.html',
                                  {'m': message},
                                  context_instance=RequestContext(request))
    raise Http404

def header_link(request):
    return '<a href="'+ reverse('wouso.interface.messaging.views.home') +'">' + _('Messages') + '</a>'
