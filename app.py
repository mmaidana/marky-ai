#!/usr/bin/env python3
import os

import aws_cdk as cdk

#from ai_marketing_gen_stack import AiMarketingGenStack
from lib.main_infrastructure import MainInfrastructureStack

app = cdk.App()


# Correctly instantiate stacks
#AiMarketingGenStack(app, "ai-marketing-gen-stack")
MainInfrastructureStack(app, "lib/main-infrastructure")

app.synth()
