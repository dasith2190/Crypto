from django.shortcuts import render
from bank.models import *
from django.template import RequestContext
from Crypto.PublicKey import RSA
from django.http import HttpResponse
import Crypto
from Crypto import Random
import ast
from base64 import b64decode
from base64 import b64encode
import re
from Crypto import Random
import cPickle
import base64
import md5
import random
from django.shortcuts import redirect
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from django.core.exceptions import ObjectDoesNotExist
from random import SystemRandom
from random import randint
from django import template
register = template.Library()


NUM_ORDERS=10
NUM_ID_STRING=5


#################################################################################################################################################

					#          METHODS USED BY BANK          #

#################################################################################################################################################


#The merchant posts' the data --message, MO signed by the bank and the identity Strings-- the bank verifies the data, if everything is valid gives the merchant. If it is not valid then it prints who cheated
def validate(request):
	code=request.POST['code'] 
	message=request.POST['message']
	ssn=request.POST['ssn']
	id_str=request.POST['id-str']
	is_valid=validate_check(code, message)

	if is_valid:
		message2=message.split(":")
		amount=message2[1].split("=")[1]
		serial=message2[2].split("=")[1]
		deposited=False
		try:
			serial=serial_numbers.objects.get(serial_number=int(serial))

			try:
				merchant=serial_number_merchant.objects.get(serial_number=serial.id, id_string=id_str)
				return HttpResponse("This money order has already been used, the merchant is cheating")
			except:
				customer=serial_number_merchant.objects.get(serial_number=serial.id)
				print customer.id_string+"-"+id_str
				id_str, valid=get_account_num(id_str, customer.id_string)
				if valid:
					return HttpResponse("This money order has already been used, the customer is cheating. The customer's ssn number is "+str(id_str))
				else:
					return HttpResponse("This money order has already been used, the merchant is cheating.")
		except ObjectDoesNotExist:
			serial=serial_numbers(serial_number=int(serial))
			serial.save()

			serial_number_merchant(serial_number=serial, merchant=ssn, id_string=id_str).save()
			deposited=True
			return HttpResponse("Here is "+amount+" in cash")

	else:
		return HttpResponse("This was not issued by our bank")
		
	return HttpResponse(is_valid)


def get_account_num(id_str1, id_str2):
	id1_spl=id_str1.split("-")
	id2_spl=id_str2.split("-")
	count=0
	ac_num=""
	valid=True
	while count<5:
		print id1_spl[count]+"#####"+(id2_spl[count])
		if (int(id1_spl[count])!=int(id2_spl[count])):
			if ac_num=="":
				ac_num=int(id1_spl[count])^int(id2_spl[count])
				print ac_num
				print "###################"
			else:
				ac_num2=int(id1_spl[count])^int(id2_spl[count])
				if ac_num!=ac_num2:
					valid=False
		count=count+1

	return ac_num, valid
				
			
	

#Bank stores the original blinded messages sent by the customer, stores it in the database and ask Alice to unblind everything except for one
def bank_create(request):
	message_id=request.POST['order_id']
	count=0

	while count<NUM_ORDERS:
		message=request.POST[str(count)]

		Server_Envelope(message=message, message_id=message_id, message_num=count).save()
		count=count+1


	num=randint(0,(NUM_ORDERS-1))
	url="/get_blind_code?id="+str(message_id)+"&num="+str(num)
	return redirect(url)

#Return the amount in each envelope message
def get_amount(cmp_str):
	msg_sp=cmp_str.split(":")
	amount=msg_sp[1].split("=")
	#print(msg_sp[1])
	return amount[1]

#Compare if the amount's in two messages are equal
def cmp_msg(amount, cmp_str):

	return int(amount)==int(get_amount(cmp_str))


#Puts the message to the original form the customer sent, that is with the identity string encrypted with Alices' public key
def encrypt_identitystring(msg):
	pt=msg.split("identity_string=")	
	ct=encrypt(pt[1], "Alice")
	p_ct=pt[0]+"identity_string="+b64encode(ct[0])
	return p_ct

#Checks if all the id strings provided are the same
def validate_idString(msg, identity):
	msg_s=msg.split("identity_string=")
	id_s=msg_s[1].split("||||")

	num_id=0
	same_id=True

	while num_id<NUM_ID_STRING:
			
		f_id=id_s[num_id].split(",")
		l_spl="L"+str(num_id)+" | "
		r_spl="R"+str(num_id)+" | "
		l_id=int(f_id[0].split(l_spl)[1])
		r_id=int(f_id[1].split(r_spl)[1])
		identity_cmp=int(l_id) ^ int(r_id)

		if int(identity) != int(identity_cmp):
			same_id=False
			break
		
		num_id=num_id+1



	return same_id

def get_identity(msg, exclude):

	msg_s=msg.split("identity_string=")
	id_s=msg_s[1].split("||||")

	f_id=id_s[0].split(",")
	l_spl="L0 |"
	r_spl="R0 | "

	l_id=int(f_id[0].split(l_spl)[1])
	r_id=int(f_id[1].split(r_spl)[1])
	identity=int(l_id) ^ int(r_id)
	
	return identity

#Bank Verifies that all the data in the envelopes are valid
def verify_issue(request):
	#Gets the excluded message number
	exclude=int(request.POST['except'])
	#Get the message id
	message_id=request.POST['order_id']


	#print  request.POST["0_message"]
	#Gets the amount in one of the messages
	if int(exclude)!=0:
		amount=get_amount(request.POST["0_message"])
		identity=get_identity(request.POST["0_message"], exclude)
	else:
		amount=get_amount(request.POST["1_message"])
		identity=get_identity(request.POST["1_message"], exclude)	
	count=0
	
	#Get all the Envelope's initially send by the customer corrosponding to this money order request id (message_id)
	objs=Server_Envelope.objects.filter(message_id=message_id)
	public=get_publickey()
	private=get_privatekey()
	is_valid=True
	blinded_msg=""
	#print("amount")
	#print(amount)

	#Loops through all Envelope objects
	for o in objs:
		num=o.message_num
		
		#If the message number is not equal to the excluded message then verify if customer didn't cheat
		if int(num)!=exclude:
			code=str(count)+"_blinding_factor"
			msg=str(count)+"_message"


			message=(request.POST[msg])
			
			id_valid=validate_idString(message, identity)
			print id_valid

			if id_valid==False:
				return HttpResponse("The identity strings in all the messages didn't match.")

			if cmp_msg(amount, message)==False:
				return HttpResponse("The Amounts were different in one or more of the envelopes we received.")

			message=encrypt_identitystring(message)
			#messageHashed = md5.new(request.POST[msg]).digest()
			messageHashed = md5.new(message).digest()

			blindSigned=b64decode(o.message)

			#return HttpResponse(str(o.message)+" "+request.POST[msg]+" "+ )
			blindSigned = private.sign(blindSigned,private.n)[0]
			#blind_factor=float(request.POST[code])
			blind_factor=long(request.POST[code])
			
			#print "blind factor "+str(blind_factor)
			#print "message "+request.POST[msg]


			#print("factor: "+str(blind_factor))
			#print(code+str(o.message_num))
			unblind = public.unblind(blindSigned,blind_factor)
			verify = public.verify(messageHashed, (unblind,))
			print verify


			if verify==False:
				is_valid=False
				break
		#If the object has the number of the Envelope that was excluded, save it.
		else:
			blinded_msg=o.message

			####################################################
			####################################################

		count=count+1
	

	#If all messages were valid, then sign it and send it to Alice
	if is_valid:
		blindSigned=b64decode(blinded_msg)
		#print("is valid encoded message-----------: "+str(blindSigned))
		blindSigned = private.sign(blindSigned,private.n)[0]
		#print("Signed message: ################"+str(blindSigned))
		url="/wallet?signed="+str(blindSigned)+"&exclude="+str(exclude)+"&msg_id="+str(message_id)
		return redirect(url)
	else:
		return HttpResponse("The blinding factor provided isn't valid.")


def merchant_deposit_bank(request):
	return render(request, 'merchant_bank.html', context={})


#################################################################################################################################################

					#            METHODS USED BY CUSTOMER          #

#################################################################################################################################################

#After customer initally request the money order, this method gets all the data, create N copies, blinds it, and sends it to the bank 
def process_data(request):

	count=0
	message=request.POST['message']
	amt=request.POST['amt']
	
	############################################# 12/02

	account_nm=request.POST['account-nm']

	############################################# end 12/02

	pub=get_publickey()

	priv=get_privatekey()

	mes_id=randint(100000,10000000)
	arr={}


	while count<NUM_ORDERS:
		id_string=""
		id_num=0
		while id_num<NUM_ID_STRING:
			rgt_hlf, lft_hlf=generate_identityString(account_nm)
			id_string=id_string+" L"+str(id_num)+" | "+str(lft_hlf)+", R"+str(id_num)+" | "+str(rgt_hlf)+" ||||"
		

			id_num=id_num+1


		serial=random.randint(10000000,1000000000)
		#print ("Length of Message: "+str(len(id_string)))

		id_string=encrypt(id_string, "Alice")
		#print id_string[0]
		#print id_string
		id_string=b64encode(id_string[0])
		mes="message="+message+" : amount="+str(amt)+" : serial="+str(serial)+" : identity_string="+id_string
		r = SystemRandom().randrange(pub.n >> 10, pub.n)
		mes2 = md5.new(mes).digest()
		msg_blinded = pub.blind(mes2, r)
		msg_blinded=b64encode(msg_blinded)


		arr[count]=msg_blinded
		#print("Blinded after decode: "+msg_blinded)
		#print("factor: "+str(r))
		#print("          ")
		############################
		'''blindSigned=b64decode(msg_blinded)
		blindSigned = priv.sign(blindSigned,priv.n)[0]
		unblind = pub.unblind(blindSigned, r)
		verify = pub.verify(mes2, (unblind,))
		print(verify)'''
		############################

		Envelope(message=mes, msg_blinded=msg_blinded , blinding_factor=str(r), message_id=mes_id, message_num=count).save()
		#Test(md5=b64encode(mes2), message_id=mes_id, message_num=count, blinded_mes=msg_blinded).save()
		#cipher=encrypt(mes)
		count=count+1
	return render(request, 'post_bank.html', context={'arr': arr, 'mes_id': mes_id})



#Generate the right and left halves of the identity strings
def generate_identityString(account_num):
	rgt_hlf=random.randint(100000, 1000000)
	lft_hlf=xor_two(account_num, rgt_hlf)
	return rgt_hlf, lft_hlf

#The bank signs and send the money order to this method, this method unblinds the message and gives it to the customer. The bank sends the message id and the excluded request from the 100 envelopes. Alice unblinds it and she can use it.		
def wallet_unblind(request):
	signed=request.GET['signed']
	exclude=request.GET['exclude']
	msg_id=request.GET['msg_id']
	#print NUM_ORDERS
	public=get_publickey()

	#Gets the message corresponding to the signed money order
	msg=Envelope.objects.get(message_id=msg_id, message_num=exclude)

	#Gets the blind factor
	blindFactor=long(str(msg.blinding_factor))

	msg2=msg.message

	pubKey=get_publickey()
	
	#print msg2
	#Hashes the message in the database
	messageHashed = md5.new(str(msg2)).digest()
	#unblinds the money order sent by the bank
	unblind = public.unblind(long(signed),blindFactor)
	
	#verify if the bank didn't cheat
	verify = public.verify(messageHashed, (unblind,))

	#print msg.msg_blinded


	#print("Verify: "+str(verify))
	

	return HttpResponse("This is your bank issued anonymous money order: <br/>"+str(unblind)+"<br/><br/>The corresponding message is:<br/>"+str(msg.message)+"<br/>"+str(verify))

	

#The bank calls this method to get all the codes for everything except for the one that they will sign
def get_codes(request):
	order_id=request.GET['id']
	num=request.GET['num']
	ord_obj=Envelope.objects.filter(message_id=order_id)
	codes={}
	pri=""

	for order in ord_obj:
		key=order.message_num
		codes[(key)]={}
		

		if int(order.message_num)!=int(num):


			new_message=alter_message(order.message)
			
			#print(long(order.blinding_factor))
			#print(order.message_num)
			codes[(key)]['blinding_factor']=str(order.blinding_factor)
			codes[(key)]['message']=new_message
		else:
			print("Rand")
			#print("MESSAGE NOT PASSED: "+order.message)
			#print("MESSAGE NOT PASSED: "+order.msg_blinded)
			#print("BLINDING FACTOR: "+str(order.blinding_factor))


	#return HttpResponse("Just checking")

	return render(request, 'post_blinding_codes.html', context={'codes': codes, 'mes_id': order_id, 'except': num})


#Decrypts the message that was encrypted by the customers' public key
def alter_message(message):
	ct=message.split("identity_string=")
	pt=ct[0]
	pt=pt+"identity_string="+str(decrypt(b64decode(ct[1]), "Alice"))
	return pt
		
	
#################################################################################################################################################

					#          METHODS USED BY MERCHANT          #

#################################################################################################################################################

def show_id(request):
	line1=request.POST['L1']
	line2=request.POST['L2']
	line3=request.POST['L3']
	line4=request.POST['L4']
	line5=request.POST['L5']
	message=request.POST['msg']
	msg=message.split("identity_string=")
	code=request.POST['code']
	pt=decrypt(b64decode(msg[1]), "Alice")


	id_string=""
	id_string2=""

	count=1
	try:
		id_spl=pt.split("||||")

	except:
		return HttpResponse("The decrypted message was not valid.")




	#return HttpResponse(str(str(line5)=="R4"))
	
	while count<=5:

		#return HttpResponse(id_spl[0])
		spl_line=id_spl[count-1].split(",")
		#return HttpResponse(line1+" L0")  |||| line1 R1 714808 |||| line2 R2 842346 |||| line3 R3 971962 |||| line4 R4 399111 ||||


		if count==1:
			if str(line1)=="L0":

				spl_line=spl_line[0].split("|")
				id_string=id_string+str(spl_line[1])

			else:
				spl_line=spl_line[1].split("|")
				id_string=id_string+str(spl_line[1])
				#id_string2=id_string+" "+str(count) L0 | 10502356, R0 | 732627


		if count==2:
			if str(line2)=="L1":
				spl_line=spl_line[0].split("|")
				id_string=id_string+"-"+str(spl_line[1])

			else:
				spl_line=spl_line[1].split("|")
				id_string=id_string+"-"+str(spl_line[1])
				#id_string2=id_string+" "+str(count) L0 | 10502356, R0 | 732627


		if count==3:
			if str(line3)=="L2":
				spl_line=spl_line[0].split("|")
				id_string=id_string+"-"+str(spl_line[1])

			else:
				spl_line=spl_line[1].split("|")
				id_string=id_string+"-"+str(spl_line[1])
		if count==4:
			if str(line4)=="L3":
				spl_line=spl_line[0].split("|")
				id_string=id_string+"-"+str(spl_line[1])

			else:
				spl_line=spl_line[1].split("|")
				id_string=id_string+"-"+str(spl_line[1])
				#id_string2=id_string+" "+str(count) L0 | 10502356, R0 | 732627

		if count==5:
			if str(line5)=="L4":
				spl_line=spl_line[0].split("|")
				id_string=id_string+"-"+str(spl_line[1])

			else:
				spl_line=spl_line[1].split("|")
				id_string=id_string+"-"+str(spl_line[1])
				return HttpResponse(id_string)
				#id_string2=id_string+" "+str(count) L0 | 10502356, R0 | 

		#id_string=id_string+ " |||| "
		count=count+1

		
	return HttpResponse("Identity String:<br/>"+id_string+"<br/><br/>Signed Message: "+str(code)+"<br/><br/>Message:<br/>"+message)

def merchant_deposit(request):
	return render(request, 'merchant.html', context={})

def merchant_verify(request):
	code=request.POST['code'] 
	message=request.POST['message']
	is_valid=validate_check(code, message)

	if is_valid:
		return render(request, 'merchant_show_id.html', context={'message': message, 'code' : code})
	else:
		return HttpResponse("The money order is invalid.")
		
	

#################################################################################################################################################

					#         COMMON METHODS         #

#################################################################################################################################################

#Validates to see if the check was signed by the bank, using the banks' public key
def validate_check(money_order, pt):
    	#message = decode_base64(money_order)
	pubKey=get_publickey()

	messageHashed = md5.new(str(pt)).digest()
	verify = pubKey.verify(messageHashed, (long(money_order),))

	return verify

#XOR two numbers and returning it
def xor_two(num1, num2):
	return int(num1) ^ int(num2)
		

#decode invalid characters
def decode_base64(data):
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)



#When passing content as a get request from a url, it is necessary to replace special characters like ($-_.+!*',) with somethind else
#this method does that
def delimit_url(text):
	text=text.replace("$", "DOLLAR")
	text=text.replace("-", "DASH")
	text=text.replace("_", "UNDERSCORE")
	text=text.replace(".", "DOT")
	text=text.replace("+", "PLUS")

	text=text.replace("!", "EXCLAIM")

	text=text.replace("*", "STAR")
	text=text.replace("'", "SINGLEQUOTE")
	text=text.replace("(", "OPENPARAM")
	text=text.replace(")", "CLOSEPARAM")
	text=text.replace(",", "COMMA")

	return text

#Does opposite of delimit_url method
def remove_delimit_url(cipher):
	cipher=cipher.replace("PLUS", "+")

	cipher=cipher.replace("DOLLAR","$")
	cipher=cipher.replace("DASH", "-")
	cipher=cipher.replace( "UNDERSCORE","_")
	cipher=cipher.replace("DOT",".")


	cipher=cipher.replace("EXCLAIM","!")

	cipher=cipher.replace( "STAR","*")
	cipher=cipher.replace("SINGLEQUOTE","'")
	cipher=cipher.replace("OPENPARAM","(")
	cipher=cipher.replace( "CLOSEPARAM",")")
	cipher=cipher.replace("COMMA",",")

	return cipher


#Method to Encrypt message using Banks' public key
def encrypt(message, entity="bank"):
	if entity=="bank":
		keyPub=get_publickey()
	else:
		keyPub=get_publickeyAlice()
	cipher = keyPub.encrypt(str(message), 320L)
	return cipher
	
#Method to decrypt message using Banks' private key
def decrypt(encrypted, entity="Alice"):
	if entity=="bank":
		keyPriv=get_privatekey()
	else:
		keyPriv=get_privatekeyAlice()

	decrypted = keyPriv.decrypt(encrypted)
	#decrypted=re.sub(r'[^\x00-\x7F]+',' ', decrypted)

	return decrypted
	
#Method to create an account
def create_account(request):
	return render(request, 'input.html', context={})



#Gets the public key of the bank
def get_publickey():
	key64=b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbbUFcBLb2dAWeZcM8YmYqA2sG nchR0N9yDFJd95FrBEwqHqxeCyJarx8O98Sn/7Cy3IE7W5wkvlFKkn1zmFkm/lK8VYRGqg2ZvdnJ6HLcIwzqEOS9at/4gdSE/7DdXvq9iYGx1pcPoEeXgt3WlVNpxCjalbrINAS1W6+wnmDf/wIDAQAB'

	keyDER = b64decode(key64)
	keypub = RSA.importKey(keyDER)
	return keypub

#Gets the private key of the bank
def get_privatekey():
	key64="MIICXQIBAAKBgQCbbUFcBLb2dAWeZcM8YmYqA2sGnchR0N9yDFJd95FrBEwqHqxeCyJarx8O98Sn/7Cy3IE7W5wkvlFKkn1zmFkm/lK8VYRGqg2ZvdnJ6HLcIwzqEOS9 at/4gdSE/7DdXvq9iYGx1pcPoEeXgt3WlVNpxCjalbrINAS1W6+wnmDf/wIDAQAB AoGBAJcgiOjcfLru3XfDIy9XzlcTs8FfMiS7oEjYyk4sJu2T5CsgYCGhWeorVVvMdx+Tc1C3L8FztkPT+l80SV9Yx3WpzE8t4rK80ZWWTqAoiGfXiAIovr+NtNAyH27I xI7HAYw8a6+G9OOHWf/EnBtUQZsHASY2EZl84NcEVd/3nkVhAkEAuLCcJqYlZgbS u4MX2VOtfEw+fn4xTG9Gq1gcSaQVQdti0smFZU78HsOfoW8RcqgINRrBTwv4igmu s4RsNfcgpQJBANdwLawnCKpi+S2MUzB2nSDIkcsvkrSbOPPpDMciXVXD9ImIanWa Pp5vIUO+w2YDGzR4wwkKsnz+Rb2BZb7jmNMCQGrm3xuH4/HQVT3wPWewBaUCxNGW3ZYueqtHDuiZLyy1fdggiTQAqfJsrQNWNLU3CbkjSW0lsrDDtfl21uPNrXkCQQCVKq3k8c31M7w2BmAfQTGAXn9cAR+B/6vKbkWTp76aQKiTham4rcjHqEiPAImIm4P9q9PW8dot41zkXrDVH/9TAkA/qRRUKgrBvDDxAXgoyijqZt3xOMTySk5gEw7Z/5ej4sM4M4aTT79ZV00rkbPMJm5w1OZbbBLaCW7ikLvA/hoh"
	keyDER = b64decode(key64)
	keyPriv = RSA.importKey(keyDER)
	return keyPriv



def get_publickey():
	key64=b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbbUFcBLb2dAWeZcM8YmYqA2sG nchR0N9yDFJd95FrBEwqHqxeCyJarx8O98Sn/7Cy3IE7W5wkvlFKkn1zmFkm/lK8VYRGqg2ZvdnJ6HLcIwzqEOS9at/4gdSE/7DdXvq9iYGx1pcPoEeXgt3WlVNpxCjalbrINAS1W6+wnmDf/wIDAQAB'

	keyDER = b64decode(key64)
	keypub = RSA.importKey(keyDER)
	return keypub

#Gets the private key of the bank
def get_privatekeyAlice():
	key64="MIIEpQIBAAKCAQEA4C+fVs5OIR+IzLQRVOaBavXruoK5qeLsMLwAaKUzNIJwPjfn Un0whdxgSr5GqIVJHOUMkqRRPYhIaSgXgKeylD91czOzGeBeIDtDmofL+ofk4k6u6MNOX7PC5yIW/wfffYBs5Rh3o6AOX7cVSerd/IRQamZQfT65470bC5860ShSce/U 9gJJTY2VsHMhLKVKcRDx/DzLpHDh5+PnzR9WHYkhPUAJoBZyv/UtUN7lY8YroRUoZ0Pdnl6jNVpycKe8Anr6IlJ9vKz27RGxrjIwExk4B3UNVdy3QZFqFaQ1BBkZ46ua s3gJ3tRKFpPMngMeSR4KeGYXQrpG8zP9DS9wYwIDAQABAoIBAQDFMV5ojoMuo3xDAsiT80U2/iVhIweIpW+31kZNxbHqqClusOGqLy/1LskMNZ4VMVgEMH0Ep8BF7ZAz 3u39XoS33bHDqWAKjM5+b2KhlH0ZW1s6rJcxakmP6KCxiczMevJchBBE22aw6GJ8UqBJKmwkZ4YMcP6vi/ManQYjDOZBfh65xA8IFiTxZ4StOLHDrY/FNCTwH9S++FWg tJM8KLT9dKIhhf8g5lJZ3g3lAVyHHPVarMlJZRDHHNbwhxXLoXL2pWKH3vlglOcvbJq3QyqH66bPndLhMLi4gnBq6geVxKqL0OUknV41Dwq96/7+Ny8C+d/xSqDwJL/L IJJhNi5hAoGBAOw+3116voBadcfgg59YWCL7nXl6Q8dh4avEAfjDemqE3Um9u5im ATk5V/dPXjUxO36BjZQoJClQPcCBWBBlLRdUi3d33WpzKQoQKrgGhIdmE1yBWZsG AMMSonq6OEhC4VvRr+sP0ZthYeyqICTQWkukjGD0HFCp6JNhd2x3FgwLAoGBAPLu mZbXrLW9gc7NwOHZRzb0Qb/zoTCIPb64RRKWlvY+s0lcrrBqYwPKRhlv83zQavvj eGQx/HFcv+Vn8gxFKSr9UczONXDL87+C0KwioSwIZeJduAfHeNwrnYLuV55rEC55 4odRbdePTW9wxiC11nO47lbyRx583pkcaAw9WYwJAoGAJXBpUZUsL4cmd0CbW1tS zGh3slKv/x8B9oifj17bPZpEv3T0D+Lu+rSdvjGzylY9CXVajIo4ANwYjTNyU1bV aIcbexlh24bYkCGzw2o1AogotVZCbxDqef+wBCcS2FDRCg4XBPeCzk8Gh80GPw9N 4AL5xDuraRUkKIcft+6/bbUCgYEAs4YNrII/mKKt/dThWEWIMh05RY/WK5ZTAtEM AluUve7B8VHzql1ERLXDLeMkbbVbij+kZW7nHiMrkG1LWzP041cGjzJIHc4ql/kl GkARGQgvuqQFboJDV3lH0k0uJNz7vUzHUbakVKsKz3Loh525GBWu1EQAuJAQs9dhMMJZnXkCgYEAq9mJ2I9gJcMwRcjW/CSdk8KYbw6vqqyorvOBU0FYqRqyE1X36ZGO 51kIYnhalKgymaoaL9uFxzjFKcTkY/L2iAoDim67uLdOhm0/O7DM7HVqbsm2NOwo 8boIPLJODSzQOTPDgkLrcTnP50oAtLBdcdNfrvK+gpjLb754wUMpiok="
	keyDER = b64decode(key64)
	keyPriv = RSA.importKey(keyDER)
	return keyPriv


def get_publickeyAlice():
	key64=b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4C+fVs5OIR+IzLQRVOaB avXruoK5qeLsMLwAaKUzNIJwPjfnUn0whdxgSr5GqIVJHOUMkqRRPYhIaSgXgKeylD91czOzGeBeIDtDmofL+ofk4k6u6MNOX7PC5yIW/wfffYBs5Rh3o6AOX7cVSerd/IRQamZQfT65470bC5860ShSce/U9gJJTY2VsHMhLKVKcRDx/DzLpHDh5+PnzR9W HYkhPUAJoBZyv/UtUN7lY8YroRUoZ0Pdnl6jNVpycKe8Anr6IlJ9vKz27RGxrjIwExk4B3UNVdy3QZFqFaQ1BBkZ46uas3gJ3tRKFpPMngMeSR4KeGYXQrpG8zP9DS9wYwIDAQAB'

	keyDER = b64decode(key64)
	keypub = RSA.importKey(keyDER)
	return keypub

#################################################################################################################################################
					
						#  IRRELEVANT TO PROJECT  #

#################################################################################################################################################
def test_alice(request):
	message="HELLO I AM JUST TESTING ALICES' PUBLIC KEY AND PRIVATE KEY asdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA BBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCcDDDDDD"

	ct=encrypt(message, "Alice")
	pt=decrypt(b64decode("w+O9EHmENBEw2L6FTuHfg9WAJWnaINBTHyl+oV5lEjU1FiDV7G07y7i+/u1aW2uZbP125F5u2dgbfuv+aOE6Td8MlXVExO+b6nYazfaqFo7Mph03H2gGXbdJsXW7UTDBFISM9GqbY838RN8KuJHf/S5d9eo4KkQB4+sPMLxXoFKAMmkwaTjLP1MaJJxbXzACtyz5SP0HtMtwKW/WtAoMsVmzd6bmTdQI4G48M+7ELoVHDS+/GoSeE4GRAz1jaauFkzyANRC4191HxnI+s5eUa86OW2wI55kvkPHYrMQaNjc1er+pOfre6znqweRebeB/HwzPlMLNEnlJJr4ZZa/PzA=="), "Alice")

	return HttpResponse(pt+ " "+str(len(message)))

def create_user(request):
	public_key, private_key=get_keys()

	return HttpResponse(public_key+"<br/><br/><br/><br/>"+private_key)

def get_keys():
	RSAkey = RSA.generate(2048)
	public_key=RSAkey.publickey().exportKey()
	private_key=RSAkey.exportKey()

	return public_key, private_key






