from django.db import models

# Create your models here.
class user_account(models.Model):
	user_name=models.CharField(max_length=200)
	balance=models.FloatField()


class serial_numbers(models.Model):
	serial_number=models.IntegerField()

class Envelope(models.Model):
	message=models.CharField(max_length=2000)
	blinding_factor=models.CharField(max_length=4000)
	msg_blinded=models.CharField(max_length=4000)
	message_id=models.IntegerField()
	message_num=models.IntegerField()

class Server_Envelope(models.Model):
	message=models.CharField(max_length=2000)
	message_id=models.IntegerField()
	message_num=models.IntegerField()

class Test(models.Model):
	md5=models.CharField(max_length=2000)
	blinded_mes=models.CharField(max_length=2000)
	message=models.CharField(max_length=2000)
	factor=models.CharField(max_length=2000)
	message_id=models.IntegerField()
	message_num=models.IntegerField()

class serial_number_merchant(models.Model):
	serial_number=models.ForeignKey(serial_numbers)
	merchant=models.CharField(max_length=9)
	id_string=models.CharField(max_length=500)

