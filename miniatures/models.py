from django.db import models
from django.utils.text import slugify
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.urls import reverse

class Miniature(models.Model):
    CATEGORY_CHOICES = [
        ('locomotive', 'Locomotive'),
        ('passenger_car', 'Passenger Car'),
        ('freight_car', 'Freight Car'),
        ('railcar', 'Railcar'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    year_of_production = models.CharField(max_length=50)
    era_livery = models.CharField(max_length=100)
    visual_characteristics = models.TextField()
    technical_characteristics = models.TextField()
    article = models.TextField()
    history = models.TextField()
    thumbnail = models.ImageField(upload_to='miniatures/thumbnails/', blank=True, null=True)
    main_image = models.ImageField(upload_to='miniatures/main/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    qr_code = models.ImageField(upload_to='miniatures/qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        # Generate slug from name if not exists
        if not self.slug:
            self.slug = slugify(self.name)

        # Generate QR code if not exists
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.get_absolute_url())
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to RGB mode
            qr_image = qr_image.convert('RGB')
            
            # Create a new image with white background
            qr_offset = Image.new('RGB', (350, 350), 'white')
            
            # Calculate the position to center the QR code
            qr_size = qr_image.size
            x = (350 - qr_size[0]) // 2
            y = (350 - qr_size[1]) // 2
            
            # Create a 4-item box for the paste operation
            box = (x, y, x + qr_size[0], y + qr_size[1])
            
            # Paste the QR code at the calculated position
            qr_offset.paste(qr_image, box)
            
            stream = BytesIO()
            qr_offset.save(stream, 'PNG')
            self.qr_code.save(f'qr_{self.slug}.png', File(stream), save=False)
            stream.close()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        url = reverse('miniature_detail', kwargs={'slug': self.slug})
        return f"https://railfans.info{url}"

    def __str__(self):
        return self.name

class Gallery(models.Model):
    miniature = models.ForeignKey(Miniature, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='miniatures/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Gallery images'

    def __str__(self):
        return f"{self.miniature.name} - {self.caption or 'Gallery Image'}"
