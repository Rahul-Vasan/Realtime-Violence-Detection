## Realtime Violence Detection, Alert and Analysis

<p align="center"><img src = "https://github.com/Rahul-Vasan/Realtime-Violence-Detection/blob/main/images/surveilance.webp" width = 700><p>

## Full Presentation video link

https://www.youtube.com/watch?v=HiT5dHDHZEk

 ## Table of Contents

- [Problem Statement](#problemstatement)
- [Solution Architecture](#architecture)
- [Features that constitute the solution](#features)
- [Why use AWS for this project?](#why)
- [End to End Product Demo](#demo)
- [Challenges Faced](#challenges)
- [References](#references)
- [Contact Me](#contact) 

***
<a id='problemstatement'></a>
## Problem Statement

The idea of project is to detect violence and perform analytics on it. We support violence being detected 2 forms:

1) Realtime violence detection on surveilance cameras 
2) Violence detection on recorded videos.

On detection of violence,we wish to alert the police in a timely manner and also push these crime events to the backend data storage and perform analytics on them to gain insights.


<a id='architecture'></a>
## Solution Architecture

<p align="center"><img src = "https://github.com/Rahul-Vasan/Realtime-Violence-Detection/blob/main/images/architecture.png" width = 700><p>

The architecture has 3 main features:

1) Live monitoring for real time surveilance
2) Uploaded video violence detection for recorded videos
3) Analytics using Lex bot and Kibana

<a id='features'></a>

## Features that constitute the solution

1) The Live Monitoring feature continuously monitors the video stream from a IP surveillance camera. It uses the deep learning model that we trained using AWS            sagemaker. When violence is detected in the live stream it alerts to the Police with the URL of the camera and the location of the camera using AWS Simple Email        Service. When the user wishes to stop the monitoring, the violent frames that we captured during the monitor are stored in S3 and the S3 URL is sent as evidence in    another email using the AWS Simple Notification Service.

2) The Uploaded Video Violence detection feature intends to reduce the human effort in detecting violence in long cumbersome videos. It pretty much follows the same      flow except that the video is uploaded from the users system,also additionally this feature uses AWS Rekognition to find the type of crime if violence was detected. 
   Both the above features pushes the crime metadata to Elasticsearch. This acts as the data source for analytics using lex bot on which we serve the customers with      customized crime analysis graphs.

3) Finally we have also provided a Kibana dashboard with summary statistics on the entire crime data and the users can create new visualizations, edit existing            visualizations with custom filters etc.


<a id='why'></a>

## Why use AWS for this project?

1)First of all our business logic and the webserver is hosted on EC2. EC2 provides on demand infrastructure that is optimized for deep learning workloads.
 
2)Sagemaker takes care of the infrastructure that is required for training and testing heavy deep learning models.
 
3)The data we mostly deal with are Frames and Videos and S3 proves to be one of the best for blob type storage.
 
4)The most critical feature of the project is the alert system. It can really make or break the purpose of saving lives. Hence it needs to be highly available and scalable and This is where SNS and SES come to the resque.
 
5)Data ingestion into Elasticsearch need not be real time hence we decouple it from business logic and make asynchronous and event driven using SQS and lambda triggers.
 
6)Lex with its NLU capabilities helps us serve the users with analytics by making the entire user experience interactive.


<a id='demo'></a>

## End to End Product Demo

https://www.youtube.com/watch?v=F7TO270YHhY

 
 <a id='challenges'></a>
 
 ## Challenges
 
 1) The major challenge was hyperparameter tuning to reduce the false positivity rate to the minimum.
 2) Building a highly available alerting mechanism.
 3) Leveraging the NLU capabilities of Amazon Lex.
 
 
 <a id='references'></a>
 
 ## Data Sources
 
 https://www.kaggle.com/datasets/odins0n/ucf-crime-dataset
 https://www.kaggle.com/datasets/mohamedmustafa/real-life-violence-situations-dataset
 https://data.cityofnewyork.us/Public-Safety/NYC-crime/qb7u-rbmr

 ## Similar Products
 
 https://appsource.microsoft.com/en-us/product/web-apps/oddityaibv1590144351772.violence_detection?tab=overview
 https://www.abtosoftware.com/blog/violence-detection
 https://zeroeyes.com
 
 
 <a id='contact'></a>
 
 ## Contact Me

  Please feel free to contact me for anything in pertinance to the project. 
  
| Contact Method |  |
| --- | --- |
| Personal Email | rahulvasan30@gmail.com |
| School Email |   rs7671@nyu.edu |
| LinkedIn | https://www.linkedin.com/in/rahul-vasan/ |
 





