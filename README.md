# Backend for Jertap 
### Python 3.10

### Install postgis according to your postgresql version 

### Setup steps
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver
- sudo apt-get install gdal-bin (if you face problem regarding GDAL path)


### Environment variables
- DEBUG
- ENABLE_API_DOCS
- DEFAULT_DATABASES
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- USE_S3
- AWS_STORAGE_BUCKET_NAME
- AWS_S3_REGION_NAME
- AWS_S3_ENDPOINT_URL
- GOOGLE_CLIENT_ID
- SOCIAL_SECRET


### API documentation url
- /api/docs/

