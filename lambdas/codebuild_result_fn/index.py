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
            before_commit_id = item['value']
        if item['name'] == 'destinationCommit':
            after_commit_id = item['value']

    build_id_arn = event['detail']['build-id']
    build_id = build_id_arn.split("/", 1)[-1]

    log_link = event['detail']['additional-information']['logs']['deep-link']
    for phase in event['detail']['additional-information']['phases']:
        if phase.get('phase-status') == 'FAILED':
            content = f'💥 {build_id} **Failed** - See the [Logs]({log_link})'
            break
        else:
            content = f'✔️ {build_id} **Succeed** - See the [Logs]({log_link})'
    codecommit_client.post_comment_for_pull_request(
        pullRequestId=pull_request_id,
        repositoryName=repository_name,
        beforeCommitId=before_commit_id,
        afterCommitId=after_commit_id,
        content=content
    )
