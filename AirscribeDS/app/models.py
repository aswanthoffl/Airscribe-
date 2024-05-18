from django.db import models

# Create your models here.

class Login(models.Model):
    Username=models.CharField(max_length=50)
    Password=models.CharField(max_length=50)
    Type=models.CharField(max_length=20)
    status_choice=(('Accepted','Accepted'),('Rejected','Rejected'),('Pending','Pending'))
    Status=models.CharField(choices=status_choice,default='Pending',max_length=20)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)


class User(models.Model):
    login=models.ForeignKey(Login,on_delete=models.CASCADE)
    Name=models.CharField(max_length=50)
    Email=models.CharField(max_length=50)
    Phone=models.CharField(max_length=10)
    Dob=models.CharField(max_length=200)
    Gender=models.CharField(max_length=10)  
    Password=models.CharField(max_length=50)  
    Confirm_password=models.CharField(max_length=50)

    
class Review(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    review=models.CharField(max_length=200,null=True,blank=True)
    rating=models.IntegerField(null=True,blank=True)
    date=models.DateTimeField(auto_now=True)


