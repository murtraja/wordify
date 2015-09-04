from django.conf import settings

def settings_variables(request):
    context_dict = {'MY_PREFIX':settings.MY_PREFIX}
    return context_dict
