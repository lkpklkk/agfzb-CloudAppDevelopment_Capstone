from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarDealer

# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .restapi import get_dealers_from_cf, get_dealer_reviews_from_cf, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/about.html", context)


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, "djangoapp/contact.html")


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]
        password = request.POST["psw"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("djangoapp:index")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("djangoapp:index")
    else:
        return render(request, "djangoapp/index.html", context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)
    elif request.method == "POST":
        # print the post parameters
        print(request.POST)
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["fname"]
        last_name = request.POST["lname"]

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.save()
        return redirect("djangoapp:index")


def get_dealerships(request):
    if request.method == "GET":
        url = "http://127.0.0.1:3000/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = " ".join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context = dict()
        context["dealership_list"] = dealerships

        return render(request, "djangoapp/index.html", context)


def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "http://127.0.0.1:5000/api/get_reviews"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        # Concat all dealer's short name
        dealer_names = " ".join([dealer.name for dealer in reviews])
        # Return a list of dealer short name
        print(reviews)
        return render(
            request,
            "djangoapp/dealer_details.html",
            {"reviews": reviews, "dealer_id": dealer_id},
        )


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        cars = CarModel.objects.filter(dealerId=dealer_id)
        context = {
            "cars": cars,
            "dealer_id": dealer_id,
        }
        return render(request, "djangoapp/add_review.html", context)
    if request.method == "POST":
        url = "http://127.0.0.1:5000/api/post_review"
        review = {}
        input_data = request.POST
        review["dealership"] = int(dealer_id)
        review["review"] = input_data["content"]
        review["purchase"] = input_data.get("purchasecheck", False)
        review["purchase_date"] = input_data["purchasedate"]
        car = CarModel.objects.get(pk=input_data["car"])
        if car:
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
        else:
            review["car_make"] = "None"
            review["car_model"] = "None"
            review["car_year"] = "None"
        review["name"] = "name"
        review["id"] = 1
        json_payload = {"review": review}
        post_review(url, json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
