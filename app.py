#!/usr/bin/env python3
import os

import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
from lib.shared_constructs.mediator import MediatorStack as MediatorStackClass  # Renamed to avoid naming conflict
from lib.consumers.niche_finder import NicheFinderStack


app = cdk.App()

# Instantiate stacks
main_infrastructure_stack = MainInfrastructureStack(app, "MainInfrastructureStack")  # MainInfrastructureStack(app, "MainInfrastructureStack", config_data)
mediator_stack = MediatorStackClass(app, "MediatorStack")  # Instantiate the MediatorStack
niche_finder_stack = NicheFinderStack(app, "NicheFinderStack",mediator_stack=mediator_stack)  # NicheFinderStack(app, "NicheFinderStack", config_data)



app.synth()
