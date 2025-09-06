#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.yedamo_stack import YedamoStack

app = cdk.App()
YedamoStack(app, "YedamoStack")
app.synth()