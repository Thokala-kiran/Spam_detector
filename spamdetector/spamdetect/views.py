from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import *
from .serializers import *
from django.contrib import messages
from django.contrib.auth.models import auth,User
# Create your views here.


class RegisterView(APIView):
    def post(self,request):

        username = request.data.get("user_name")
        userphone = request.data.get("user_phone")
        email = request.data.get("email",None)
        password1 = request.data.get("password")
        password2 = request.data.get("confirm_password")

        if(password1!=password2):
            
            return Response({"MSG": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if User.objects.filter(username = username).exists():

                return Response({"MSG":"User Already exists"},status = status.HTTP_400_BAD_REQUEST)
            else:
                User.objects.create_user(user_name=username,user_phone = userphone,email = email, password=password1)
                return Response({"MSG": "User created successfully"}, status=status.HTTP_201_CREATED)
            

    
class LoginView(APIView):

    def post(self,request):

        username = request.data.get("user_name")
        password = request.data.get("password")

        user = auth.authenticate(username=username, password=password)

        if user :
            auth.login(request,user)
        else:
            return Response({"Msg":"Invalid Credentials"},status=status.HTTP_404_NOT_FOUND)

    
class LogoutView(APIView):

    def post(self,request):
        auth.logout(request)
        Response({"MSG" : "Successfully logged out"},status=status.HTTP_200_OK)


class AddView(APIView):

    def post(self,request):

        temp = userserializer(request.data)
        if temp.is_valid():
            temp.save()
        else:
            Response({"Msg":"Invalid data"},status=status.HTTP_400_BAD_REQUEST)
class SearchView(APIView):

    def post(self,request,key):

        if type(key) == str : #search by name 
            names = userprofile.objects.filter(Q(name__icontains=key))  # Matches if key is anywhere in the name

        # Sort results: key at the start of the name first, then elsewhere
            sorted_names = sorted(
                names,
                key=lambda x: (
                    not x.name.lower().startswith(key.lower()),  # False (0) if it starts with key, True (1) otherwise
                    x.name.lower()  # Then sort alphabetically
                )
            )
            users  = userserializer(sorted_names,many = True)
            return Response({"Msg":"Successful Search","Users" : users.data},status=status.HTTP_200_OK)
        
        elif type(key) == int: #search by phone number
            registered_user = User.objects.filter(userprofile__contact=key).first()
            if registered_user:
                user_data = userserializer(registered_user.userprofile).data
                
                # Show email only if searching user is in their contact list
                searching_user = request.user
                if not userprofile.objects.filter(user=registered_user, contacts__contact=searching_user.userprofile.contact).exists():
                    user_data.pop("email", None)  # Remove email if not in contact list
                
                return Response({"Msg": "Successful Search", "User": user_data}, status=status.HTTP_200_OK)

            # Case 2: Search globally for the phone number
            non_registered_users = userprofile.objects.filter(contact=key)
            global_results = userserializer(non_registered_users, many=True)
            return Response({"Msg": "Global Search Results", "Users": global_results.data}, status=status.HTTP_200_OK)
            
        else:
            Response({"Msg":"UnSuccessful Search"},status=status.HTTP_400_BAD_REQUEST)




