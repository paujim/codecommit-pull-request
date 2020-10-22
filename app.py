#!/usr/bin/env python3

from aws_cdk import core

from codecommit_pull_request.codecommit_pull_request_stack import CodecommitPullRequestStack


app = core.App()
CodecommitPullRequestStack(app, "codecommit-pull-request")

app.synth()
