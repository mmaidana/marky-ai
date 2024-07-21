#!/usr/bin/env python3
import os

import aws_cdk as cdk
from infra.lib.shared_constructs.common_resource import CommonResourceStack as CommonStackClass  # Renamed to avoid naming conflict
from infra.lib.main_infrastructure import MainInfrastructureStack
from infra.lib.shared_constructs.mediator import MediatorStack as MediatorStackClass  # Renamed to avoid naming conflict
from infra.lib.consumers.niche_finder import NicheFinderStack


app = cdk.App()

# Instantiate stacks
common_stack = CommonStackClass(app, "CommonResourceStack")
main_infrastructure_stack = MainInfrastructureStack(app, "MainInfrastructureStack",common_stack=common_stack)  # MainInfrastructureStack(app, "MainInfrastructureStack", config_data)
mediator_stack = MediatorStackClass(app, "MediatorStack",common_stack=common_stack)  # Instantiate the MediatorStack
niche_finder_stack = NicheFinderStack(app, "NicheFinderStack", common_stack=common_stack, mediator_stack=mediator_stack)  # NicheFinderStack(app, "NicheFinderStack", config_data)



app.synth()
