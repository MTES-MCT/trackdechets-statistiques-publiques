from django.views.generic import TemplateView


class Main(TemplateView):
    template_name = "stats/main.html"
