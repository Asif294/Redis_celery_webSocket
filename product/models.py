from django.db import models

class Products(models.Model):
    name=models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand=models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Course(models.Model):
    title =models.CharField(max_length=150)
    price =models.DecimalField(max_digits=8 ,decimal_places=2)
    description=models.TextField()
    category=models.CharField(max_length=100)
    is_featured=models.BooleanField(default=True)
    is_paid=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
