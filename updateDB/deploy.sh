gcloud functions deploy 'updateBabyNameData'\
 --runtime 'python39'\
 --memory '1024MB'\
 --service-account='name-genderator@portfolio-334101.iam.gserviceaccount.com'\
 --trigger-topic 'updateBabyNameData'\
 --entry-point 'main'\
 --region='us-west1'\
 --timeout=540
