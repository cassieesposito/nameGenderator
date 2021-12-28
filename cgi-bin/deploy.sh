gcloud functions deploy 'nameGenderator'\
 --runtime 'python39'\
 --service-account='name-genderator@portfolio-334101.iam.gserviceaccount.com'\
 --allow-unauthenticated\
 --trigger-http\
 --entry-point 'main'\
 --region='us-west1'
