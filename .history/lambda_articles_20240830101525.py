import boto3
import json
import os

# Initialize S3 and DynamoDB clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables for S3 bucket name and DynamoDB table name
BUCKET_NAME = os.environ['S3_BUCKET_NAME']  # e.g., 'dyadichealth-articles'
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']  # e.g., 'ArticlesMetadata'

def lambda_handler(event, context):
    try:
        # Fetching the list of articles from S3
        articles = fetch_articles_from_s3()

        # Fetching additional metadata from DynamoDB if necessary
        enriched_articles = enrich_articles_with_metadata(articles)

        return {
            'statusCode': 200,
            'body': json.dumps(enriched_articles)
        }
    except Exception as e:
        print(f'Error fetching articles: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to fetch articles'})
        }

# Function to fetch articles from S3
def fetch_articles_from_s3():
    articles = []

    for i in range(1, 17):  # Assuming 16 articles as per your use case
        key = f'ArticleContent/article{i}.json'
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            article = json.loads(response['Body'].read().decode('utf-8'))
            articles.append(article)
        except Exception as e:
            print(f'Failed to fetch {key}: {str(e)}')
            # Continue even if some articles fail to load

    return articles

# Function to enrich articles with additional metadata from DynamoDB
def enrich_articles_with_metadata(articles):
    table = dynamodb.Table(TABLE_NAME)
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
