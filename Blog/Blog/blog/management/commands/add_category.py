from blog.models import Category
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'This command inserts post data'

    def handle(self, *args, **options):

        Category.objects.all().delete()
        
        categories = ['Sports', 'Action', 'Tech', 'Science', 'Art']

        for category_name in categories:
            Category.objects.create(name = category_name)
          
        self.stdout.write(self.style.SUCCESS("Completed inserting data"))
