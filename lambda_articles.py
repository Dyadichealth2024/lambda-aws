import boto3
import json
import os
from datetime import datetime

# Initialize S3 and DynamoDB clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables for S3 bucket name and DynamoDB table names
BUCKET_NAME = os.environ['S3_BUCKET_NAME']  # e.g., 'dyadichealth-articles'
ARTICLE_METADATA_TABLE_NAME = os.environ['DYNAMODB_METADATA_TABLE_NAME']  # e.g., 'ArticlesMetadata'
LAST_CHECKED_TABLE_NAME = os.environ['DYNAMODB_LAST_CHECKED_TABLE_NAME']  # e.g., 'LastCheckedDates'

def lambda_handler(event, context):
    try:
        # Fetching the list of articles and their metadata from S3
        articles, updates = fetch_articles_from_s3()

        # Fetching additional metadata from DynamoDB if necessary
        enriched_articles = enrich_articles_with_metadata(articles)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'updated_articles': updates,
                'enriched_articles': enriched_articles
            })
        }
    except Exception as e:
        print(f'Error fetching articles: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to fetch articles'})
        }

# Function to fetch articles and check for updates in S3
def fetch_articles_from_s3():
    articles = []
    updates = []

    for i in range(1, 17):  # Assuming 16 articles as per your use case
        key = f'ArticleContent/article{i}.json'
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            article = json.loads(response['Body'].read().decode('utf-8'))
            articles.append(article)

            # Check if this article has been updated
            last_modified = response['LastModified']
            if is_article_updated(article['id'], last_modified):
                updates.append(article)

        except Exception as e:
            print(f'Failed to fetch {key}: {str(e)}')
            # Continue even if some articles fail to load

    return articles, updates

# Function to check if an article has been updated based on last modified timestamp
def is_article_updated(article_id, last_modified):
    last_checked_date = get_last_checked_date(article_id)

    if not last_checked_date or last_modified > last_checked_date:
        update_last_checked_date(article_id, last_modified)
        return True
    return False

# Function to get the last checked date for an article
def get_last_checked_date(article_id):
    table = dynamodb.Table(LAST_CHECKED_TABLE_NAME)
    try:
        response = table.get_item(Key={'ArticleID': article_id})
        if 'Item' in response:
            return response['Item']['LastChecked']
        else:
            return None
    except Exception as e:
        print(f'Failed to get last checked date for article ID {article_id}: {str(e)}')
        return None

# Function to update the last checked date for an article
def update_last_checked_date(article_id, last_modified):
    table = dynamodb.Table(LAST_CHECKED_TABLE_NAME)
    try:
        table.put_item(
            Item={
                'ArticleID': article_id,
                'LastChecked': last_modified.isoformat()  # Store as ISO formatted string
            }
        )
    except Exception as e:
        print(f'Failed to update last checked date for article ID {article_id}: {str(e)}')

# Function to enrich articles with additional metadata from DynamoDB
def enrich_articles_with_metadata(articles):
    table = dynamodb.Table(ARTICLE_METADATA_TABLE_NAME)
    enriched_articles = []

    for article in articles:
        try:
            response = table.get_item(Key={'ArticleID': article['id']})  # Assuming 'id' is a key in your article data
            item = response.get('Item')
            if item:
                enriched_article = {**article, **item}
                enriched_articles.append(enriched_article)
            else:
                enriched_articles.append(article)
        except Exception as e:
            print(f'Failed to fetch metadata for article ID {article["id"]}: {str(e)}')
            enriched_articles.append(article)

    return enriched_articles
