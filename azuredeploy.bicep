@description('Enter suffix to be included in the name of the resources.')
@minLength(2)
@maxLength(12)
param suffix string = 'callcenter'

@description('Location for all resources. Ensure the region supports Azure OpenAI service.')
@allowed([
'eastus' 
'southcentral'
'westeurope'])
param location string = 'eastus'

@description('SKU of App Service Plan.')
@allowed([
  'F1'
  'D1'
  'B1'
  'B2'
  'B3'
  'S1'
  'S2'
  'S3'
  'P1'
  'P2'
  'P3'
  'P4'
])
param appservicesku string = 'B1'

@description('The Runtime stack of current web app')
param linuxFxVersion string = 'PYTHON|3.11'

@description('Git Repo URL where the code is available. Use original repo or fork it and use your own.')
param repoUrl string = 'https://github.com/richardsonbq/aoai_callcenter.git'

@description('Git Repo branch to deploy')
param repoBranch string = 'main'

@description('SKU of Azure Speech Service. Free (F0) tier should be fine')
param speechServiceSku string = 'F0'

@description('SKU of Azure OpenAI Service. Currently, only S0 is available')
param openAiServiceSku string = 'S0'

@allowed([
  'text-curie-001'
  'text-davinci-002'
  'text-davinci-003'
  'gpt-35-turbo'
])
@description('Model and version of the Azure OpenAI completion model to be used. Ensure the selected model is supported in the region.')
param openAICompletionModel string = 'text-davinci-002'

@description('Name of the Azure OpenAI completion model to be used. You can customize your name or keep the suggested default')
param openAICompletionModelName string = openAICompletionModel


var uuid = uniqueString(guid(resourceGroup().id))
var uniqueName = '${suffix}-${uuid}'

//Defining the names of the resources
var appServicePlanPortalName = 'AppServicePlan-${uniqueName}'
var webAppName = 'webapp-${uniqueName}'
var azopenaiName = 'azopenai-${uniqueName}'
var speechName = 'speech-${uniqueName}'

//Ensure all pre-reqs are met and start streamlit application
var startupCommand = '/home/startup.sh\npython -m streamlit run app/app.py --server.port 8000 --server.address 0.0.0.0'


resource speechAccount 'Microsoft.CognitiveServices/accounts@2021-04-30' = {  
  name: speechName 
  location: location  
  kind: 'SpeechServices'  
  sku: {  
    name: speechServiceSku  
  }  
  properties: {  
  }  
}  

//Azure OpenAI deployment
resource openAiAccount 'Microsoft.CognitiveServices/accounts@2021-04-30' = {  
  name: azopenaiName  
  location: location  
  kind: 'OpenAI'  
  sku: {  
    name: openAiServiceSku  
  }  
  properties: {
    publicNetworkAccess: 'Enabled'
  }  
}

resource openAICompletionModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2022-12-01' = {
  parent: openAiAccount
  name: openAICompletionModelName
  properties: {
    model: {
      format: 'OpenAI'
      name: openAICompletionModel
      version: '1'
    }
    scaleSettings: {
      scaleType: 'Standard'
    }
  }
}

resource appServicePlanPortal 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanPortalName
  location: location
  sku: {
    name: appservicesku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2020-06-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlanPortal.id
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      appSettings: [  
        {  
          name: 'OPENAI_API_KEY'  
          value: openAiAccount.listKeys().key1  
        }
        {  
          name: 'OPENAI_API_ENDPOINT'  
          value: openAiAccount.properties.endpoint
        }  
        {  
          name: 'SPEECH_API_KEY'  
          value: speechAccount.listKeys().key1  
        }
        {  
          name: 'SPEECH_API_REGION'  
          value: speechAccount.location  
        } 
      ]
    }
  }
}

resource webAppName_web 'Microsoft.Web/sites/sourcecontrols@2020-06-01' = {
  parent: webApp
  name: 'web'
  properties: {
    repoUrl: repoUrl
    branch: repoBranch
    isManualIntegration: true
  }
}

resource Microsoft_Web_sites_config_webAppName_web 'Microsoft.Web/sites/config@2021-03-01' = {
  parent: webApp
  name: 'web'
  properties: {
    appCommandLine: startupCommand
  }
}
