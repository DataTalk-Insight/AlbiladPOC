# RecSys
Recommender System project

# How to run

```bash
>> git clone  git@github.com:DataTalk-Insight/AlbiladPOC.git
>> cd AlbiladPOC
>> pip install -r requirements.txt
>> python app.py
```
- You can access the application here [link]( http://127.0.0.1:8050/)

# How to deploy on GCP
- Get [gcp cli](https://cloud.google.com/sdk/docs/quickstart)

## Make a Project on GCP
- Using  the Console Interface online (which we use below), create a new project with a suitable project name (here we call it map-app).

- Deploy Using gcloud Command Line Tool
Next, check your project is active in gcloud using:

```bash
>> gcloud config get-value project
```
Which will print the following on screen:

Your active configuration is: [default]

my-project-id

To change the project to your desired project, type:

```bash
>> gcloud config set project albiladpoc
```
Next, to deploy, type:

```bash
>> gcloud app deploy
```
Then select your desired region (we use us-central)