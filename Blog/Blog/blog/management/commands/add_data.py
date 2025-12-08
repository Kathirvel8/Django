from blog.models import Post, Category
from django.core.management.base import BaseCommand
import random

class Command(BaseCommand):
    help = 'This command inserts post data'

    def handle(self, *args, **options):

        Post.objects.all().delete()
        
        titles = ['Naruto',
         'Bleach',
         'Demon Slayer',
         'Monster',
         'One Piece']

        contents = ['Best one',
                  'Ultimate one',
                  'Best Animated',
                  'Psycological',
                  'Long run']

        image_urls = [
                  "https://picsum.photos/id/1/800/400",
                  "https://picsum.photos/id/2/800/400",
                  "https://picsum.photos/id/3/800/400",
                  "https://picsum.photos/id/4/800/400",
                  "https://picsum.photos/id/5/800/400",
        ]

        categories = Category.objects.all()

        for title, content, img_url in zip(titles, contents, image_urls):
            category = random.choice(categories)
            Post.objects.create(content= content, title= title, img_url = img_url, category = category)
          
        self.stdout.write(self.style.SUCCESS("Completed inserting data"))
