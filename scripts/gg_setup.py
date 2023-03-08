import boto3
import subprocess
import json
import os
import requests
import sys
import time


# User input from the start.sh script
deviceName = sys.argv[1]
groupName = sys.argv[2]
roleAliasName = sys.argv[3]
roleName = sys.argv[4]
maxDuration = sys.argv[5]
deviceRegion = sys.argv[6]

##### !!!!! ADMIN POLICY ARN !!!!! #####
policyArn = 'arn:aws:iam::aws:policy/AdministratorAccess'

# Create boto clients
iam_client = boto3.client('iam')
iot_client = boto3.client('iot')
sts_client = boto3.client('sts')

def convert_JSON_to_string(fileName, *args):

    # convert json object from file to python dict
    with open(fileName) as f:
        data = json.load(f)

    # convert dict to string
    stringData = json.dumps(data)
    
    newString = ''
    argIndex = 0
    # .format is annoying when working with JSON, wrote this section to deal with it
    for index, char in enumerate(stringData):
        if stringData[index] == '{' and stringData[index + 1] == '}':
            newString += args[argIndex]
            argIndex += 1
        else:
            newString += stringData[index]

    # return the JSON object as a string with the variable data
    return newString
    

####################### IAM ####################################

##### !!!!!!! THIS IS AN ADMIN MANAGED POLICY !!!!!!! #########
#### !!!!!!! CHANGE TO THE BOTO3 PutRolePolicy API call to add inline custom policies !!!!! ########

def rolePermissions():
    response = iam_client.attach_role_policy(
    RoleName=roleName,
    PolicyArn=policyArn #### REPLACE THIS
    )
    time.sleep(2)
    print("\n\n**********************************************\n\n")
    print("ADDED ADMIN PERMISSIONS TO YOUR ROLE!")
    print("\n\n**********************************************\n\n")
    print("waiting.")
    print("waiting..")
    print("waiting...")
    print("waiting....")
    time.sleep(5)

#### ^^^^^^^ REPLACE THAT ######################

# Create a custom role 
def createRole():
    try:
        response = iam_client.create_role(
            RoleName=roleName,
            AssumeRolePolicyDocument=convert_JSON_to_string('iam_create_role_policy.json'),
            Description='IoT Greengrass Role',
            MaxSessionDuration=maxDuration,
            Tags=[
                {
                    'Key': 'IoT',
                    'Value': 'Jesse Richey'
                },
            ]
        )
        roleInfo = response['Role']
        print("\n\nRole {} created successfully, Role ARN is {}\n\n".format(roleInfo['RoleName'], roleInfo['Arn']))
        rolePermissions()
        print("\n\nRole provided with ADMIN RIGHTS ----- Change this for real environments.\n\n")
    except Exception as e:
        print(e)
        pass

def getRoleArn():

    try:
        response = iam_client.get_role(
            RoleName=roleName # iotAdmin
        )
        return response['Role']['Arn']

    except Exception as e:
        print(e)
        pass



####################### IAM ####################################


####################### IOT ####################################

# fix the class stuff and investigate why self.aliasArn is required
def createRoleAlias():

    try:
        response = iot_client.create_role_alias(
            roleAlias=roleAliasName,
            roleArn=getRoleArn(),
            credentialDurationSeconds=maxDuration, # 3600 to 43200 seconds, must match role
            tags=[
                {
                    'Key': 'raspberryPi',
                    'Value': 'MPU6050'
                },
            ]
        )
        print("Role alias {} created sucessfully!".format(response['roleAlias']))
        

    except Exception as e:
        print(e)
        pass

def getCredentialsEndpointId():

    response = iot_client.describe_endpoint(
        endpointType = "iot:CredentialProvider"
    )

    return response['endpointAddress']

def attachThingCertificate(certId):
    
    response = iot_client.attach_thing_principal(
        thingName=deviceName,
        principal=certId
    )
    if response == {}:
        print("Attached certificate {} to {}.\n".format(certId, thingName))

    
# ask for advice on permissions so you don't look stupid
def createCerts():

    response = iot_client.create_keys_and_certificate(
        setAsActive=True
    )
    certificateArn = response['certificateArn']
    certificateId = response['certificateId']
    deviceCert = response['certificatePem']
    publicKey = response['keyPair']['PublicKey']
    privateKey = response['keyPair']['PrivateKey']

    rootResponse = requests.get('https://www.amazontrust.com/repository/AmazonRootCA1.pem')
    # create the certs directory

    with open('/home/pi/certs/AmazonRootCA1.pem', 'wb') as f:
        f.write(rootResponse.content)

    with open('/home/pi/certs/myDeviceCertificate.pem', 'w') as f:
        f.write(deviceCert)
    
    with open('/home/pi/certs/myPublicKey.public.key', 'w') as f:
        f.write(publicKey)

    with open('/home/pi/certs/myPrivateKey.private.key', 'w') as f:
        f.write(privateKey)

    bashCommand = ['sudo', 'chmod', '-R', '644', '/home/pi/certs']
    result = subprocess.run(bashCommand, stdout=subprocess.PIPE)

    attachThingCertificate(certificateArn)

    return certificateArn

def createDeviceCertificatePolicy():
    try:
        response = iot_client.create_policy(
            policyName=groupName,
            policyDocument=convert_JSON_to_string('iot_create_role_policy.json', deviceRegion, getAccountId(), roleAliasName),
            tags=[
                {
                    'Key': 'IoT',
                    'Value': 'MPU6050'
                }
            ]
        )
        return response['policyName']
    except Exception as e:
        print(e)
        pass
    

def attachPolicyToDeviceCertificate():
    
    response = iot_client.attach_policy(
        policyName=createDeviceCertificatePolicy(),
        target=createCerts()
    )

####################### IOT ####################################

def getAccountId():

    response = sts_client.get_caller_identity()
    return response['Account']

# Order is alphabetical
def getCerts():
    certPath = '/home/pi/certs/'
    absolutePathCerts = []
    certFiles = os.listdir(certPath)
    for item in certFiles:
        absolutePathCerts.append(certPath + item)
    return absolutePathCerts


##### SEE TOKEN EXCHANGE SERVICE DEPENDENCY BELOW ######
# REPLACED CUSTOM CRED GENERATOR FOR NATIVE TES BELOW
##### SEE TOKEN EXCHANGE SERVICE DEPENDENCY BELOW ######

def main():
    createRole()
    createRoleAlias()
    attachPolicyToDeviceCertificate()
    # getCreds()

if __name__ == '__main__':
    main()



###### Assign this to Role trust relationship
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "",
#             "Effect": "Allow",
#             "Principal": {
#                 "Service": "credentials.iot.amazonaws.com"
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }


####### Attach this policy to the certificate on the device
# {
#    "Version":"2012-10-17",
#    "Statement":[
#       {
#          "Effect":"Allow",
#          "Action":"iot:AssumeRoleWithCertificate",
#          "Resource":"arn:aws:iot:your region:your_aws_account_id:rolealias/your role alias"
#       }
#    ]
# }

############ I guess there is an easier way #############
# {
#   "RecipeFormatVersion": "2020-01-25",
#   "ComponentName": "com.example.ListS3Buckets",
#   "ComponentVersion": "1.0.0",
#   "ComponentDescription": "A component that uses the token exchange service to list S3 buckets.",
#   "ComponentPublisher": "Amazon",
#   "ComponentDependencies": {                          ##### <---- This hard dependency creates a token exchange service
#     "aws.greengrass.TokenExchangeService": {          ##### <---- It handles the creation of credentials based on the role/role-alias
#       "VersionRequirement": "^2.0.0",
#       "DependencyType": "HARD"
#     }
#   },
#   "Manifests": [
#     {
#       "Platform": {
#         "os": "linux"
#       },
#       "Lifecycle": {
#         "Install": "pip3 install --user boto3",
#         "Run": "python3 -u {artifacts:path}/list_s3_buckets.py"
#       }
#     },
#     {
#       "Platform": {
#         "os": "windows"
#       },
#       "Lifecycle": {
#         "Install": "pip3 install --user boto3",
#         "Run": "py -3 -u {artifacts:path}/list_s3_buckets.py"
#       }
#     }
#   ]
# }

# def getCreds(): 
#     privateKey, publicKey, deviceCertificate, rootCA = getCerts()
#     headers = {
#         'x-amzn-iot-thingname': deviceName,
#     }

#     cert = (deviceCertificate, privateKey)

#     response = requests.get('https://{}/role-aliases/{}/credentials'.format(getCredentialsEndpointId(), aliasName), headers=headers, cert=cert, verify=rootCA)

#     credDict = json.loads(response.text)
#     creds = credDict["credentials"]
#     accessKey = creds["accessKeyId"]
#     secretKey = creds["secretAccessKey"]
#     sessionToken = creds["sessionToken"]

#     setCredEnvVariables(accessKey, secretKey, sessionToken)

# def setCredEnvVariables(accessKey, secretAccessKey, sessionToken):
#     os.environ["AWS_ACCESS_KEY_ID"] = accessKey
#     os.environ["AWS_SECRET_ACCESS_KEY"] = secretAccessKey
#     os.environ["AWS_SESSION_TOKEN"] = sessionToken

#     print("""
#     AWS_ACCESS_KEY_ID: {}
#     AWS_SECRET_ACCESS_KEY: {}
#     AWS_SESSION_TOKEN: {}\n
#     """.format(accessKey, secretAccessKey, sessionToken))