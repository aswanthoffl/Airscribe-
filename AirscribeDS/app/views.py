from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Login,User,Review
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.utils import timezone
import cv2
import numpy as np
from .HandTrackingModule import handDetector
import keyboard
import pygame
import time
import pyttsx3
import os
import base64
import io
import re
from PIL import Image
from tensorflow.keras.models import load_model
# Create your views here.


### build paths inside the project

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


###landing page###
def landing(request):
    return render(request,'landing_page.html')

def logins(request):
        if request.method=='POST':
            username=request.POST['username']
            password=request.POST['password']
            try:
                data = Login.objects.get(Username=username,Password=password)
                if data is not None:
                    request.session['id'] = data.id
                    if data.Type=='Admin':
                        return redirect(admin_home)
                    elif data.Type=='User' and data.Status=='Accepted':
                        data.last_login = timezone.now()
                        data.save()
                        return redirect(user_home)
                    else:
                        return render(request, 'login.html',{'error':'Wait for Admin approvel'})

                else:
                    return render(request, 'login.html',{'error':'invalid credentials'})
            except Exception as e:
                return render(request, 'login.html',{'error':e})
        else:
            return render(request,'login.html')
    



def logout(request):
    if 'id' in request.session:
        # Retrieve the user object based on the stored session id
        user_id = request.session['id']
        try:
            user = Login.objects.get(id=user_id)
            # Update the last_logout field for the user
            user.last_logout = timezone.now()
            user.save()
        except Login.DoesNotExist:
            pass  # Handle the case where the user doesn't exist or has been deleted

        # Clear the session
        request.session.flush()
    
    # Redirect the user to the landing page
    return redirect(landing)


def user_registeration(request):
    if 'id' in request.session:
        if request.method=='POST':
            Name=request.POST['Name']
            Email=request.POST['Email']
            if Login.objects.filter(Username=Email):
                return render(request,'user_registeration.html',{'x':'Email already Exist!!!'})
            Phone=request.POST['Phone']
            Dob=request.POST['Dob']
            Gender=request.POST['gender']
            Password=request.POST['Password']
            Confirm_password=request.POST['Confirm_password']

            if Password!=Confirm_password:
                return render(request,'user_registeration.html',{'x':'Password not matching!!!'})
            data1=Login.objects.create(Username=Email,Password=Password,Type='User')
            data1.save()

            data2=User.objects.create(login=data1,
                                    Name=Name,
                                    Email=Email,
                                    Phone=Phone,
                                    Dob=Dob,
                                    Gender=Gender,
                                    Password=Password,
                                    Confirm_password=Confirm_password
                                    )
            data2.save()
            return render(request,'login.html')
        else:
            return render(request,'user_registeration.html')
    else:
        return redirect(logins)
    
####ADMIN####

def admin_home(request):
    if 'id' in request.session:
        return render(request,'admin_home.html')
    else:
        return redirect(logins)

def view_users(request):
    if 'id' in request.session:
        data1=User.objects.filter(login__Status="Accepted")
        return render(request,'view_users.html',{'data':data1})

def verify_users(request):
    if 'id' in request.session:
        data=User.objects.all()
        return render(request,'verify_user.html',{'data':data})
    else:
        return redirect(logins)



def user_status(request,id):
    if 'id' in request.session:
        data=Login.objects.get(id=id)
        if request.method=='POST':
            data1=request.POST['Status']
            if data1=='Accepted':
                data.Status='Accepted'
            elif data1=='Rejected':
                data.Status='Rejected'
            data.save() 
        return redirect(verify_users)
    else:
        return redirect(logins)
    

def change_password(request):
    if 'id' in request.session:
        data=request.session['id']
        data1=Login.objects.get(id=data)
        if request.method=='POST':
            newpwd=request.POST['newpwd']
            confpwd=request.POST['confpwd']
            if newpwd!=confpwd:
                    return render(request,'change_password.html',{'x':'Password not matching!!!'})
            else:
                data1.Password=newpwd
                data1.save()
                return render(request,'change_password.html',{'x':'Password Successfully changed'})
        else:
            return render(request,'change_password.html')
    else:
        return redirect(logins)

def view_review(request):
    if 'id' in request.session:
        content=Review.objects.all()
        items_per_page = 5
        paginator = Paginator(content, items_per_page)
        page = request.GET.get('page', 1)

        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        return render(request,'view_review.html',{'data':data})
    else:
        return redirect(logins)
    

def view_login_details(request):
    if 'id' in request.session:
        data1=User.objects.filter(login__Status="Accepted")
        return render(request,'userlogin_details.html',{'data':data1})



    
####user


def user_home(request):
    if 'id' in request.session:
        return render(request,'user_home.html')
    else:
        return redirect(logins)


def view_profile(request):
    if 'id' in request.session:
        data=request.session['id']
        data1=Login.objects.get(id=data)
        data2=User.objects.get(login=data1.id)
        return render(request,'view_profile.html',{'data2':data2})
    else:
        return redirect(logins)

def edit_profile(request,id):
    if 'id' in request.session:
        data=User.objects.get(id=id)
        if request.method=='POST':
            data.Name=request.POST['Name']
            data.Phone=request.POST['Phone']
            data.Dob=request.POST['Dob']
            data.Gender=request.POST['gender']
            data.save()
            return redirect(view_profile)
        else:
            return render(request,'edit_profile.html',{'data':data})
    else:
        return redirect(logins)
    

def rating(request):
    if 'id' in request.session:
        return render(request,'rating.html')   
    else:
        return redirect(logins)

def changepassword_user(request):
    if 'id' in request.session:
        data=request.session['id']
        data1=Login.objects.get(id=data)
        data2=User.objects.get(login=data1.id)
        if request.method=="POST":
            newpwd=request.POST['newpwd']
            confpwd=request.POST['confpwd']
            if newpwd!=confpwd:
                return render(request,'change_password.html',{'x':'Password not matching!!!'})
            else:
                data1.Password=newpwd
                data1.save()
                data2.Password=newpwd
                data2.Confirm_password=confpwd
                data2.save()
        return render(request,'changepassword_user.html')
    else:
        return redirect(logins)

from django.http import HttpResponseRedirect
from django.urls import reverse

def user_view_review(request):
    if 'id' in request.session:
        data = request.session['id']
        data1 = Login.objects.get(id=data)
        data2 = User.objects.get(login=data1.id)
        content = Review.objects.all()
        items_per_page = 5
        paginator = Paginator(content, items_per_page)
        page = request.GET.get('page', 1)

        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        if request.method == "POST":
            review = request.POST.get('review', None)
            rating = request.POST.get('rating', 0)

            if review or rating:
                data3 = Review.objects.create(user_id=data2, review=review, rating=rating)
                data3.save()
                # Redirect to the same page after POST request
                return render(request,'user_view_review.html',{'message':'Review/Rating added successfully!!!','reviews':data})
            else:
                return render(request, 'user_view_review.html', {'message': 'Must need to fill one content', 'reviews': data})
        else:
            return render(request, 'user_view_review.html', {'reviews': data})
    else:
        return redirect(logins)



def air_scribe(request):

    engine = pyttsx3.init()

    # Color Attributes
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (0, 0, 255)
    YELLOW =  (0, 255, 255)
    GREEN = (0, 255, 0)
    BACKGROUND = (255, 255, 255)
    FORGROUND = (0, 255, 0)
    BORDER = (255, 0, 0)
    lastdrawColor = (0, 0, 1)
    drawColor = (0, 0, 255)
    BOUNDRYINC = 5

    color_dict = {
    ord('c'): (192, 192, 192),  # Clear (Gray color)
    ord('b'): (135, 206, 235),  # Skin
    ord('g'): (0, 255, 0),       # Green
    ord('r'): (0, 0, 255),       # Red
    ord('y'): (0, 255, 255),     # Yellow
    ord('w'): (255, 255, 255),   # White
    ord('e'): (0, 0, 0)          # Eraser (Black color)
    }

    # CV2 Attributes
    cap = cv2.VideoCapture(0)
    width, height = 1280, 720
    cap.set(3, width)
    cap.set(4, height)
    imgCanvas = np.zeros((height, width, 3), np.uint8)

    # PyGame Attributes
    pygame.init()
    FONT = pygame.font.SysFont('freesansbold.tff', 18)
    DISPLAYSURF = pygame.display.set_mode((width, height), flags=pygame.HIDDEN)
    pygame.display.set_caption("Digit Board")
    number_xcord = []
    number_ycord = []


    # Prediction Model Attributes
    label = ""
    PREDICT = "off"
    model_file_path1=os.path.join(BASE_DIR,"app","alphabet.h5")
    model_file_path2=os.path.join(BASE_DIR,"app","numeric.h5")
    AlphaMODEL = load_model(model_file_path1)
    NumMODEL = load_model(model_file_path2)
    AlphaLABELS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j',
                10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't',
                20: 'u', 21: 'v', 22: 'w', 23: 'x', 24: 'y', 25: 'z', 26: ''}
    NumLABELS = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9'}
    rect_min_x, rect_max_x = 0, 0
    rect_min_y, rect_max_y = 0, 0


    # HandDetection Attributes
    detector = handDetector(detectionCon=0.85)
    x1, y1 = 0, 0
    xp, yp = 0, 0
    brushThickness = 15
    eraserThickness = 30
    modeValue = "OFF"
    modeColor = RED

    # Assuming hand_detected is set to False before hand is detected for the first time
    hand_detected=False
    recognized_characters = ""
    filename = "" 
    c=1
    # Assuming hand_detected is set to False before hand is detected for the first time
    hand_detected = False

    while True:
        SUCCESS, img = cap.read()
        img = cv2.flip(img, 1) 

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        cv2.putText(img, "Press A for Alphabet Recognition Mode ", (0, 145), 3, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img, "Press N for Digit Recognition Mode ", (0, 162), 3, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img, "Press O for Turn Off Recognition Mode ", (0, 179), 3, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img, f'{"RECOGNITION IS "}{modeValue}', (0, 196), 3, 0.5, modeColor, 1, cv2.LINE_AA)

        if keyboard.is_pressed('a'):
            if PREDICT != "alpha":
                PREDICT = "alpha"
                modeValue, modeColor = "ALPHABETS", GREEN
                engine.say("alphabet recognition mode is on")
                engine.runAndWait()

        if keyboard.is_pressed('n'):
            if PREDICT != "num":
                PREDICT = "num"
                modeValue, modeColor = "NUMBER", YELLOW
                engine.say("number recognition mode is on")
                engine.runAndWait()

        if keyboard.is_pressed('o'):
            if PREDICT != "off":
                PREDICT = "off"
                modeValue, modeColor = "OFF", RED
                engine.say("recognition mode is off")
                engine.runAndWait()

            xp, yp = 0, 0
            label = ""
            rect_min_x, rect_max_x = 0, 0
            rect_min_y, rect_max_y = 0, 0
            number_xcord = []
            number_ycord = []
            time.sleep(0.5)

        # Check if hand landmarks are detected
        if len(lmList) > 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            # Assuming hand_detected is set to True when hand is detected for the first time
            # if hand_detected == False:
            #     engine.say('hand  is detected')
            #     engine.runAndWait()
            #     hand_detected = True

            fingers = detector.fingersUp()

            if fingers[1] and fingers[2]:
                number_xcord = sorted(number_xcord)
                number_ycord = sorted(number_ycord)

                if len(number_xcord) > 0 and len(number_ycord) > 0 and PREDICT != "off":
                    if drawColor != (0, 0, 0) and lastdrawColor != (0, 0, 0):
                        rect_min_x, rect_max_x = max(number_xcord[0] - BOUNDRYINC, 0), min(width, number_xcord[-1] + BOUNDRYINC)
                        rect_min_y, rect_max_y = max(0, number_ycord[0] - BOUNDRYINC), min(number_ycord[-1] + BOUNDRYINC, height)
                        number_xcord = []
                        number_ycord = []

                        img_arr = np.array(pygame.PixelArray(DISPLAYSURF))[rect_min_x:rect_max_x, rect_min_y:rect_max_y].T.astype(np.float32)

                        cv2.rectangle(imgCanvas, (rect_min_x, rect_min_y), (rect_max_x, rect_max_y), BORDER, 3)
                        image = cv2.resize(img_arr, (28, 28))
                        image = np.pad(image, (10, 10), 'constant', constant_values=0)
                        image = cv2.resize(image, (28, 28)) / 255

                        if PREDICT == "alpha":
                            label = str(AlphaLABELS[np.argmax(AlphaMODEL.predict(image.reshape(1, 28, 28, 1)))])
                            engine.say(label)
                            engine.runAndWait()
                            recognized_characters= recognized_characters+label
                        if PREDICT == "num":
                            label = str(NumLABELS[np.argmax(NumMODEL.predict(image.reshape(1, 28, 28, 1)))])
                            engine.say(label)
                            engine.runAndWait()
                            recognized_characters= recognized_characters+label
                        pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, width, height))

                        cv2.rectangle(imgCanvas, (rect_min_x + 50, rect_min_y - 30), (rect_min_x, rect_min_y), BACKGROUND, -1)
                        cv2.putText(imgCanvas, label, (rect_min_x, rect_min_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0, 255), 2, cv2.LINE_AA)

                    else:
                        number_xcord = []
                        number_ycord = []

                xp, yp = 0, 0

                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            elif fingers[1] and fingers[2] == False:

                number_xcord.append(x1)
                number_ycord.append(y1)

                cv2.circle(img, (x1, y1 - 15), 15, drawColor, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                if drawColor == (0, 0, 0):
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                    pygame.draw.line(DISPLAYSURF, WHITE, (xp, yp), (x1, y1), brushThickness)
                xp, yp = x1, y1
            else:
                xp, yp = 0, 0
           


    # Navigation bar logic
        if y1 < 50:
            selected_option_index = int(x1 / (width / len(color_dict)))
            if selected_option_index < len(color_dict):
                selected_option_key = list(color_dict.keys())[selected_option_index]
                if selected_option_key == ord('e'):
                    drawColor = (0, 0, 0)
                elif selected_option_key == ord('c'):
                    imgCanvas = np.zeros((height, width, 3), np.uint8)  # Clear the canvas
                    recognized_characters = ""
                else:
                    drawColor = color_dict[selected_option_key]
                
                # Calculate the total width of all color rectangles
                total_rect_width = width - 60  # Width minus space for close button

            # Calculate the width of each color rectangle
            color_rect_width = total_rect_width / len(color_dict)
        # # Draw color rectangles
        for i, (key, color) in enumerate(color_dict.items()):
            rect_start_x = i * color_rect_width + 10  # Adding 10 pixels of space between rectangles
            rect_end_x = (i + 1) * color_rect_width - 10  # Subtracting 10 pixels to maintain space
            cv2.rectangle(img, (int(rect_start_x), 0), (int(rect_end_x), 50), color, 2)  # Draw border only
            color_name = 'Eraser' if color == (0, 0, 0) else 'White' if color == (255, 255, 255) else 'Red' if color == (0, 0, 255) else 'Yellow' if color == (0, 255, 255) else 'Green' if color == (0, 255, 0) else 'Skin' if color == (135, 206, 235) else 'Clear all'
            text_color = color
            text_x = int(rect_start_x) + 10  # Example x-coordinate
            text_y = 30  
            cv2.putText(img, color_name, (text_x, text_y), cv2.FONT_HERSHEY_TRIPLEX, 0.75, text_color, 1)  # Draw text


            font_scale = 0.8  # Example font scale
            font_thickness = 2  # Example font thickness
        # Draw close button
        close_rect_start_x = width - 60  # Distance from other rectangles
        close_rect_end_x = width - 10
        cv2.rectangle(img, (int(close_rect_start_x), 0), (int(close_rect_end_x), 50), (0, 0, 0), -1)  # Draw filled rectangle for close button
        cv2.putText(img, "X", (int(close_rect_start_x) + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # Draw 'X' in white color
        if x1 > width - 50 and y1 < 50:
            break

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        #-----------------------------------
        newline_added = False

        # Calculate the position and size of the space button
        space_button_width = 90 # Width of the space button
        space_button_height = 50  # Height of the space button
        space_button_x = 10  # X-coordinate of the space button
        space_button_y = height // 3 - space_button_height // 2  # Y-coordinate of the space button

        # Draw the space button
        cv2.rectangle(img, (space_button_x, space_button_y), (space_button_x + space_button_width, space_button_y + space_button_height), WHITE, -1)
        cv2.rectangle(img, (space_button_x, space_button_y), (space_button_x + space_button_width, space_button_y + space_button_height), BLACK, 2)
        cv2.putText(img, "SPACE", (space_button_x + 10, space_button_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, BLACK, 2)

        # Check if the hand is clicking on the space button
        if space_button_x < x1 < space_button_x + space_button_width and space_button_y < y1 < space_button_y + space_button_height:
            recognized_characters += "\n"
            newline_added = True




        if keyboard.is_pressed('up'):
            brushThickness += 1
        elif keyboard.is_pressed('down'):
            brushThickness = max(1, brushThickness - 1)

        # Get the width and height of the image
        img_height, img_width = img.shape[:2]

        # Define the position for the text
        text_position = (img_width - 200, img_height - 10)

        cv2.putText(img, f'Brush Thickness: {brushThickness}', text_position, cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        

        c=1
        if keyboard.is_pressed('s'):
            filename = f'canvas_image{c}.png'
            cv2.imwrite(filename, imgCanvas)
            print(f"Canvas saved as {filename}")
            
          
            c=c+1

        pygame.display.update()
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # data={
        #     'recognized_characters':recognized_characters,
        #     'saved_image':filename
        #         }
       

    cap.release()
    cv2.destroyAllWindows()
    recognized_characters = re.sub(r'\s+', '\n', recognized_characters)
    print("Recognized characters:", recognized_characters)
    return render(request,'user_home.html',{'data':recognized_characters,'saved_image':filename})
