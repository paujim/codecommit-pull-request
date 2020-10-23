import datetime
import boto3
codecommit_client = boto3.client('codecommit')


def lambda_handler(event, context):

    print(event)
    for item in event['detail']['additional-information']['environment']['environment-variables']:
        if item['name'] == 'pullRequestId':
            pull_request_id = item['value']
        if item['name'] == 'repositoryName':
            repository_name = item['value']
        if item['name'] == 'sourceCommit':
            source_commit = item['value']
        if item['name'] == 'destinationCommit':
            destination_commit = item['value']
    
    build_id_arn = event['detail']['build-id']
    build_id = build_id_arn.split("/", 1)[-1]
    
    codecommit_client.post_comment_for_pull_request(
            pullRequestId=pull_request_id,
            repositoryName=repository_name,
            beforeCommitId=source_commit,
            afterCommitId=destination_commit,
            content=f'⏳ {build_id} **Started** at {datetime.datetime.utcnow().time()}',
        )
