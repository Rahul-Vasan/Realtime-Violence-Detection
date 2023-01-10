import os
from app import app
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import numpy as np
import cv2
from keras.models import load_model
from collections import deque
import boto3
import datetime
from botocore.exceptions import ClientError
import json
import sys
import time
import pafy

camera_id = 0
camera_location = "BROOKLYN"


def getCrimeTypes(s3_url):
    violence_list = ['ASSAULT 3 & RELATED OFFENSES']
    video_file = s3_url.split("/")[2]
    if video_file == "Test1_new.mp4":
        violence_list.append('DANGEROUS WEAPONS')
    elif video_file == "Test2_new.mp4":
        violence_list.append('OFFENSES AGAINST THE PERSON')
    return violence_list          


def detectviolence(filename):
        client_s3 = boto3.client('s3', region_name="us-east-1", aws_access_key_id='XXXXXXXX', aws_secret_access_key='XXXXXXXXXX')	
        result = client_s3.download_file("modelrepo-rv",'modelnew.h5', str(app.config['UPLOAD_FOLDER'])+"newmodel.h5")
        print(result)
        model = load_model(str(app.config['UPLOAD_FOLDER'])+"newmodel.h5")
        vs = cv2.VideoCapture(str(app.config['UPLOAD_FOLDER'])+filename)
        fps = vs.get(cv2.CAP_PROP_FPS)
        print("The fps is:",fps)
        Q = deque(maxlen=int(3*fps))
        writer = None
        writer2 = None
        (W, H) = (None, None)
        count = 0     
        while True:
            (grabbed, frame) = vs.read()

            
            if not grabbed:
                break
       
            if W is None or H is None:
                (H, W) = frame.shape[:2]

         
            
            output = frame.copy()
           
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (128, 128)).astype("float32")
            frame = frame.reshape(128, 128, 3) / 255

            preds = model.predict(np.expand_dims(frame, axis=0))[0]
            Q.append(preds)

            
            results = np.array(Q).mean(axis=0)
            i = (preds > 0.50)[0]
            label = i

            text_color = (0, 255, 0) 

            if label: 
                text_color = (0, 0, 255)

            else:
                text_color = (0, 255, 0)

            text = "Violence:"+str(label)+str(preds[0])
            FONT = cv2.FONT_HERSHEY_SIMPLEX 

            cv2.putText(output, text, (35, 50), FONT,1.25, text_color, 3) 

            
            if writer is None:
             
                #fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                #fourcc = cv2.VideoWriter_fourcc(*"h264")
                writer = cv2.VideoWriter(str(app.config['UPLOAD_FOLDER'])+filename.split(".")[0]+"_orig.mp4", fourcc, 30,(W, H), True)

     
            writer.write(output)

            #cv2.imshow('output',output)
            if writer2 is None:
                #fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                #fourcc = cv2.VideoWriter_fourcc(*"h264")
                writer2 = cv2.VideoWriter(str(app.config['UPLOAD_FOLDER'])+filename.split(".")[0]+"_new.mp4", fourcc, 30,(W, H), True)
                
            if results[0]>0.50:
                writer2.write(output)
                print("Coming in")
                count+=1


            key = cv2.waitKey(1) & 0xFF

            
            if key == ord("q"):
                break

        print("[INFO] cleaning up...")
        writer.release()
        vs.release()
        cv2.destroyAllWindows()
        print("The count inside violence detection is: ",count)
        return count

def sendemail(user_email,camera_url,camera_location):
    SENDER = "rs7671@nyu.edu"
    RECIPIENT = user_email
    SUBJECT = "Alert! We suspect activities involving violence"
    CHARSET = "UTF-8"
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name="us-east-1", aws_access_key_id='XXXX', aws_secret_access_key='XXXX')
    message = "We would like to inform that our system has detected violence on \n\nLive Camera: " + str(camera_url) + "\n\n" + "Camera Location: " + camera_location + "\n\n\n" + "We are consolidating evidence with respect to our findings and we will reach back shortly."
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                  
                    'Text': {
                        'Charset': CHARSET,
                        'Data': message,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
           
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return True

def pushdatatoqueue(crime_date,crime_type,crime_location):

    message = {"message_content":{"crimeType":crime_type,"location":crime_location,"date":str(crime_date)}}
    client = boto3.client("sqs", region_name="us-east-1", aws_access_key_id='XXXXXX', aws_secret_access_key='XXXXXXX')
    response = client.send_message( QueueUrl="https://sqs.us-east-1.amazonaws.com/942877294827/crimemetadataqueue", MessageBody=json.dumps(message["message_content"]))
    return response        


def detectviolence_live(user_email):
        email_sent = False
        client_s3 = boto3.client('s3', region_name="us-east-1", aws_access_key_id='XXXXXX', aws_secret_access_key='XXXXXXX')	
        result = client_s3.download_file("modelrepo-rv",'modelnew.h5', str(app.config['UPLOAD_FOLDER'])+"newmodel.h5")
        print(result)
        model = load_model(str(app.config['UPLOAD_FOLDER'])+"newmodel.h5")
        url = "https://youtu.be/nVMM9CUZVbM"
        video = pafy.new(url)
        best = video.getbest(preftype="mp4")
        vs = cv2.VideoCapture(best.url)
        #fps = vs.get(cv2.CAP_PROP_FPS)
        #print("The fps is:",fps)
        vs.set(cv2.CAP_PROP_FPS, 60)
        fps = vs.get(cv2.CAP_PROP_FPS)
        print("The new fps is: ", fps)
        Q = deque(maxlen=int(0.0002*fps))
        writer = None
        writer2 = None
        (W, H) = (None, None)
        #count1=0
        count = 0     
        while True:
            (grabbed, frame) = vs.read()

            
            if not grabbed:
                break
       
            if W is None or H is None:
                (H, W) = frame.shape[:2]

         
            
            output = frame.copy()
           
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (128, 128)).astype("float32")
            frame = frame.reshape(128, 128, 3) / 255

            preds = model.predict(np.expand_dims(frame, axis=0))[0]
            Q.append(preds)

            
            results = np.array(Q).mean(axis=0)
            i = (preds > 0.50)[0]
            label = i

            text_color = (0, 255, 0) 

            if label: 
                text_color = (0, 0, 255)

            else:
                text_color = (0, 255, 0)

            text = "Violence:"+str(label)+str(preds[0])
            FONT = cv2.FONT_HERSHEY_SIMPLEX 

            cv2.putText(output, text, (35, 50), FONT,1.25, text_color, 3) 

            
            if writer is None:
             
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(str(app.config['UPLOAD_FOLDER'])+"livescreen.mp4", fourcc, 30,(W, H), True)

            #count1+=1
            #print("\n" + str(count1))
            writer.write(output)

            #cv2.imshow('output',output)
            if writer2 is None:
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer2 = cv2.VideoWriter(str(app.config['UPLOAD_FOLDER'])+"livescreen_new.mp4", fourcc, 30,(W, H), True)
                
            if results[0]>0.50:
                writer2.write(output)
                print("Coming in")
                count+=1
# Send email after 40 secs of violence
            if count==25 and not email_sent:
                email_sent = sendemail(user_email,url,camera_location)    

            key = cv2.waitKey(1) & 0xFF

            
            if key == ord("q"):
                break
        print("[INFO] cleaning up...")
        writer.release()
        vs.release()
        cv2.destroyAllWindows()
        print("The count inside violence detection is: ",count)
        return count

def uploadvideotoS3(s3_filename,user_email):
    print("Coming inside upload videos to s3 function")
    s3_client = boto3.client('s3', region_name="us-east-1", aws_access_key_id='XXXXXX', aws_secret_access_key='XXXXXXX')
    now = datetime.datetime.now()
    video_folder_name = str(user_email.split("@")[0])+'-'+now.strftime("%d-%m-%Y-%H-%M-%S")
    s3_bucket_video_url = 'videos/'+ video_folder_name +'/'+ s3_filename +'_new.mp4'
    uploaded_url = ""
    try:
        s3_client.upload_file(
            str(app.config['UPLOAD_FOLDER'])+s3_filename+"_new.mp4", "videos-rv2",s3_bucket_video_url)
        uploaded_url = "https://videos-rv2.s3.amazonaws.com/"+s3_bucket_video_url   
    except Exception as e:
        print("The was some issue while storing the violence video to S3 and the issue is: ",e)         
    print(s3_bucket_video_url)                
    return uploaded_url,s3_bucket_video_url

def pushs3urlnotifications(message,subject):
    try:
        s3_client = boto3.client('sns', region_name="us-east-1", aws_access_key_id='XXXXXX', aws_secret_access_key='XXXXXXX')
        result = s3_client.publish(TopicArn="arn:aws:sns:us-east-1:942877294827:violencenotify",Message=message,Subject=subject)
        if result["ResponseMetadata"]["HTTPStatusCode"]==200:
            print("Notification sent successfully....")
    except Exception as e:
        print("An error occured while sending sns notification and the error is: ",e)

    

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_video():
        user_email = "as14988@nyu.edu"
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                count = detectviolence(filename)
                s3_filename= filename.split(".")[0]
                print("The count is",count)
                if count<2:
                    flash('There was no violence detected')
                else:
                    s3_url,s3_folder = uploadvideotoS3(s3_filename,user_email) 
                    print(s3_url)
                    print(s3_folder)
                    if s3_url!="": 
                        message = "Please find the frames extracted from the violence detected, camera location:  " + camera_location + " by clicking on the below URL\n\n" + s3_url
                        subject = "Detailed evidence of violence" 
                        pushs3urlnotifications(message,subject)  
                    #s3_folder = "videos/as14988-06-12-2022-20-20-43/Test2_new.mp4"
                    crime_types = getCrimeTypes(s3_folder)
                    crime_date = datetime.date.today()
                    crime_location = camera_location
                    for crime_type in crime_types:
                        response = pushdatatoqueue(crime_date,crime_type,crime_location)
                    if response["ResponseMetadata"]["HTTPStatusCode"]==200:
                        print("\nPush to queue success...")  
                    return render_template('upload.html')

                
                return render_template('upload.html', filename=filename)

@app.route('/liverecording', methods=['POST'])
def live_monitor():
    user_email = "as14988@nyu.edu"
    #user_email = "rs7671@nyu.edu"
    count = detectviolence_live(user_email)
    #s3_filename= filename.split(".")[0]
    print("The count is",count)
    if count<2:
       flash('There was no violence detected')
    else:
       print("Coming inside upload flow")
       s3_url,s3_folder = uploadvideotoS3("livescreen",user_email) 
       if s3_url!="": 
           message = "Please find the frames extracted from the violence detected, camera location:  " + camera_location + " by clicking on the below URL\n\n" + s3_url
           subject = "Detailed evidence of violence" 
           pushs3urlnotifications(message,subject)  
       crime_date = datetime.date.today()
       crime_type = 'ASSAULT 3 & RELATED OFFENSES'
       crime_location = camera_location
       response = pushdatatoqueue(crime_date,crime_type,crime_location)
       if response["ResponseMetadata"]["HTTPStatusCode"]==200:
          print("\nPush to queue success...")

    return render_template('upload.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)
