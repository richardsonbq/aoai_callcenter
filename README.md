# Call Center Analytics Demo - Azure Cognitive Services (Speech) with Azure OpenAI Service

This sample demonstrates how to use Azure OpenAI Service to interact with audio transcriptions to analyze it, summarize, extract sentiment and even propose responses.

In this demo solution, we use Speech Service (Azure Cognitive Services) to transcribe an audio input that user can upload (or use one of the samples in [audio](https://github.com/richardsonbq/aoai_callcenter/tree/main/audio) folder), Azure OpenAI Service to interact with this transcription with several prompts (samples also available in [audio](https://github.com/richardsonbq/aoai_callcenter/tree/main/audio) folder) that the user can enter and, finally, we also use Speech Service to synthetize audio responses.


## Features

* Multi-language: you can select which language is the action and the prompts you'll enter. The solution will give all the outputs (including audio synthetization) in this language
* Visual interface to upload audio files, interact with it using Azure OpenAI and synthetize responses

## Getting Started

> **IMPORTANT:** In order to deploy and run this example, you'll need an **Azure subscription with access enabled for the Azure OpenAI service**. You can request access [here](https://aka.ms/oaiapply).

> **AZURE RESOURCE COSTS** this sample will create Azure App Service that has a monthly cost.

### Prerequisites

#### To Run Locally
- [Azure Developer CLI](https://aka.ms/azure-dev/install)
- [Python 3+](https://www.python.org/downloads/)
    - **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
    - **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
- [Git](https://git-scm.com/downloads)

#### Automated Deployment
**Will be available soon**






