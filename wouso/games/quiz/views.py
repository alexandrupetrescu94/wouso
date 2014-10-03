from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy

from models import Quiz, QuizUser, QuizGame
from forms import QuizForm
from wouso.core.ui import register_sidebar_block


@login_required
def index(request):
    """ Shows all quizzes related to the current user """
    quizzes = Quiz.objects.all()

    return render_to_response('quiz/index.html',
                              {'quizzes': quizzes},
                              context_instance=RequestContext(request))


class QuizView(View):
    def dispatch(self, request, *args, **kwargs):
        if QuizGame.disabled():
            return redirect('wouso.interface.views.homepage')

        profile = request.user.get_profile()
        # print profile, "profile"
        self.quiz_user = profile.get_extension(QuizUser)
        # print self.quiz_user, 'quiz_user'
        # print Quiz.objects.all()
        self.quiz = get_object_or_404(Quiz, pk=1)
        # self.quiz = Quiz.create('lesson-1', False)

        # Quiz.create('lesson_one', False)

        return super(QuizView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = QuizForm(self.quiz)
        return render_to_response('quiz/quiz.html',
                                  {'quiz': self.quiz, 'form': form},
                                  context_instance=RequestContext(request))

    def post(self, request, **kwargs):
        form = QuizForm(self.quiz, request.POST)
        results = form.get_response()
        form.check_self_boxes()
        print results
        if results.get('results', False):
            results['results'] = form.get_results_in_order(results['results'])
            questions_and_answers = zip(form.visible_fields(), results['results'])
        else:
            questions_and_answers = None

        print questions_and_answers, "QA"
        return reverse_lazy('index')


quiz = login_required(QuizView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    quiz_user = user.get_profile().get_extension(QuizUser)

    return render_to_string('quiz/sidebar.html',
                            {'quser': quiz_user,
                             'quiz': QuizGame,
                             'id': 'quiz'})


register_sidebar_block('quiz', sidebar_widget)
