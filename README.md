# AWS S3 Terminal Explorer

## Howto

- create the .env file with filled information from .env.example

```bash
AWS_ACCESS_KEY_ID=<your-aws-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-acess-key>
AWS_DEFAULT_REGION=<your-default-region>
AWS_BUCKET_NAME=<your-bucket-name>
PROJECT_NAME=<your-key-name>
```

- install package in your environment:

```bash
pip install boto3 simple_term_menu
```


- run explorer:
```bash
python s3_explorer.py
```

Enjoy
