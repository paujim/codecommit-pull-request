import os
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_events as events,
    aws_events_targets as targets,
)


def _create_fn_from_folder(scope, folder_name: str) -> _lambda.Function:

    fn = _lambda.Function(
        scope=scope,
        id=f"lambda-{folder_name}",
        code=_lambda.Code.from_asset(
            path=os.path.join("lambdas", folder_name)),
        runtime=_lambda.Runtime.PYTHON_3_8,
        handler="index.lambda_handler",
    )
    fn.add_to_role_policy(
        statement=iam.PolicyStatement(
            resources=[
                "*",
            ],
            actions=[
                "codecommit:PostCommentForPullRequest",
            ]
        ),
    )
    return fn


class CodecommitPullRequestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, repository_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        codebuild_start_fn = _create_fn_from_folder(
            scope=self,
            folder_name="codebuild_start_fn",
        )
        codebuild_result_fn = _create_fn_from_folder(
            scope=self,
            folder_name="codebuild_result_fn",
        )

        repo = codecommit.Repository(
            scope=self,
            id="Repository",
            repository_name=repository_name,
        )

        project = codebuild.Project(
            scope=self,
            id="PullRequestCodeCommitProject",
            source=codebuild.Source.code_commit(repository=repo),
            badge=True,
        )

        project.on_build_started(
            id="on-build-started",
            target=targets.LambdaFunction(handler=codebuild_start_fn),
        )
        project.on_build_succeeded(
            id="on-build-succeeded",
            target=targets.LambdaFunction(handler=codebuild_result_fn),
        )
        project.on_build_failed(
            id="on-build-failed",
            target=targets.LambdaFunction(handler=codebuild_result_fn),
        )

        on_pull_request_state_change_rule = repo.on_pull_request_state_change(
            id="on-pull-request-change",
            event_pattern=events.EventPattern(
                detail={"event": [
                    "pullRequestSourceBranchUpdated",
                    "pullRequestCreated",
                ]}),
            # target=targets.LambdaFunction(
            #     handler=pull_request_fn,
            # )
        )
        on_pull_request_state_change_rule.add_target(
            target=targets.CodeBuildProject(
                project=project,
                event=events.RuleTargetInput.from_object(
                    {
                        "sourceVersion": events.EventField.from_path("$.detail.sourceCommit"),
                        "artifactsOverride": {"type": "NO_ARTIFACTS"},
                        "environmentVariablesOverride": [
                            {
                                "name": "pullRequestId",
                                "value": events.EventField.from_path("$.detail.pullRequestId"),
                                "type": "PLAINTEXT"
                            },
                            {
                                "name": "repositoryName",
                                "value": events.EventField.from_path("$.detail.repositoryNames[0]"),
                                "type": "PLAINTEXT"
                            },
                            {
                                "name": "sourceCommit",
                                "value": events.EventField.from_path("$.detail.sourceCommit"),
                                "type": "PLAINTEXT"
                            },
                            {
                                "name": "destinationCommit",
                                "value": events.EventField.from_path("$.detail.destinationCommit"),
                                "type": "PLAINTEXT"
                            }
                        ]
                    }
                ),
            )
        )
