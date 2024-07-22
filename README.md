
# Marky-Ai: AI driven Affiliate Marketing Automation project!



An ai affiliate marketing solution that automate the whole process end to end from getting the niches, choosing the best affiliate programs and provide insights on what are the best campaigns with ROI and useful comprehensive financials reports and ai driven decisions 

Enjoy!


<!--
suggest an image for a system that does this?
an ai affiliate marketing solution that automate the whole process end to end from getting the niches, choosing the best affiliate programs, creates campaigns and generate content and provide insights on what are the best campaigns with ROI to simplify the whole process and useful comprehensive financials reports and ai driven decisions 
Perhaps make it look as something that streamline the whole process with ai in the center of it?

a cyborg that represents the ai that will help to simplify and accelerate affiliate marketing, by streamlining the process from getting the best niches, the best affiliate programs, campaign creation and content, and a comprehensive report that helps to drive the decisions on what campaigns are getting the most ROI

suggest an image represents the ai that will help to simplify and accelerate affiliate marketing process, by streamlining the process from getting the best niches, the best affiliate programs, campaign creation and content, and a comprehensive report that helps to drive the decisions on what campaigns are getting the most ROI

-->

Step 1

```mermaid
flowchart LR
    %% External ID: get-niches-process-flow-id-1
    Start(("Start: Step 1: Get Niche"))  -- Hourly CronJob Or Manual Calls to Lambda --> B[["Niche Lambda"]]
    B -- Add Query to Queue --> C{"Niche SQS Check the Queue"}
    C -- Previous Process Finished? --> D[["Process Niche Queue"]]
    D -- Queue is being processed --> B
    B -- Get list of niches --> E("Gemini AI")
    E -- Get Results --> F{"Lambda Processor"}
    F -- First Time? --> Q[["Lambda Settler"]]
    Q -- Save Brand New File to Bucket --> H[("Niche S3 Bucket")]
    Q -- Create Niche Repo --> I[["Github"]]
    Q -- Commit file to Repo --> I
    H -- Commit file to Repo --> I
    I -- Publish Event to Niche SNS --> T[["Niche SNS Topic"]]
    T -- Lambda Settler is subscribe to topic --> Q
    Q -- Add Niche/s to Database --> K[("Niche DynamoDB")]
    Q -- Publish Notifications --> T
    T -- Notify - File Created --> L[/"Marketeer"\]
    Q -- Clean Up --> U[["Run Clean up Process"]]
    F -- else --> N[["Lambda Parser"]]
    N -- Create Branch --> I
    N -- Save File to Bucket with New Niche --> H
    N -- Commit File to Branch --> I
    H -- Commit File to Branch --> I
    N -- Parser Review Results --> O{"Lambda Reviewer"}
    O -- New Niche? --> R>"Notify Marketeer"]
    R --> T
    T -- Notify- New Niches to Review --> L
    L -- Review Results --> I
    I -- Validate Results --> S{"Accept Results"}
    S --> L
    L -- Merge Branch --> I
    I -- Github Actions call Parser --> N
    N -- Add Niche to Database --> K
    N -- Check if the queue is empty --> M{"Is the Queue Empty?"}
    M -- Clean Up --> U
    M -- Process Next Item in Niche Queue --> D
    U -- Trigger Step 2 --> End((("End Step 1")))
    %%subgraph Step 2
    %%End-->StartA(("Start Step 2: Get Affiliate Program"))
    %%end
    classDef processStyle stroke-width:2px,stroke-dasharray: 2,stroke:#000000,fill:#FFD600;
    class T,U,N,Q,B,D processStyle;
    classDef startEndStyle stroke:none,fill:#4CAF50,color:#FFFFFF,stroke-width:4px,stroke-dasharray: 0;
    class Start,End,StartA startEndStyle;
    classDef labelStyle fill:#FFE0B2,stroke:#000000
    class R labelStyle
    classDef decisionStyle color:#FFFFFF,fill:#D50000,stroke-width:4px,stroke-dasharray: 5,stroke:#000000
    class F,C,M,O decisionStyle
    classDef dbStyle stroke:#000000,fill:#BBDEFB
    class K,H dbStyle
    style E fill:#2962FF,color:#FFFFFF
    style I stroke-width:1px,stroke-dasharray: 0,fill:#000000,color:#FFFFFF
    style L stroke-width:4px,stroke-dasharray: 5,stroke:#000000,fill:#FF6D00
```