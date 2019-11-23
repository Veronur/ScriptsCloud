import os
import boto3
from botocore.exceptions import ClientError
import time


ec2 = boto3.client('ec2',region_name='us-east-2')

instancia = ec2.describe_instances(
    Filters=[
        {
            'Name': 'tag:Owner',
            'Values': ['Lucca Delchairo Costabile']
        }
    ]  
)


def geraKeyPair():
    chaves = ec2.describe_key_pairs()['KeyPairs']
    k=0
    for i in chaves: 
        if i['KeyName']=="Aps3Delch":
            response = ec2.delete_key_pair(KeyName='Aps3Delch')
            response = ec2.create_key_pair(KeyName='Aps3Delch') 
            f= open("Aps3Delch.pem","w+")
            f.write(response['KeyMaterial'])
            #f.close()
            #os.chmod("Aps3Delch.pem", 400)
            break
        k+=1
    if k == len(chaves):
        response = ec2.create_key_pair(KeyName='Aps3Delch')
        f= open("Aps3Delch.pem","w+")
        f.write(response['KeyMaterial'])
        #f.close()
        #os.chmod("Aps3Delch.pem", 400)
    return response

def createSecurityGroup(DB,WS):
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        SG = ec2.describe_security_groups()['SecurityGroups']
        #print(response)
    except ClientError as e:
        #print('2')
        print(e)

    k=0
    for i in SG: 
        if i['GroupName']=='APS_DelchDB' or i['GroupName']=='APS_DelchWS':
            try:
                response = ec2.delete_security_group(GroupName='APS_DelchDB')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)
            try:
                response = ec2.delete_security_group(GroupName='APS_DelchWS')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)        
            try:
                responseDB = ec2.create_security_group(GroupName='APS_DelchDB',
                                                    Description='Security group do DataBase',
                                                    VpcId=vpc_id)
                responseWS = ec2.create_security_group(GroupName='APS_DelchWS',
                                                    Description='Security group do webServer',
                                                    VpcId=vpc_id)           
                security_group_idDB = responseDB['GroupId']
                security_group_idWS = responseWS['GroupId']
                data = ec2.authorize_security_group_ingress(
                    GroupId=security_group_idDB,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp':'{}/32'.format(WS['PublicIp'])}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2.authorize_security_group_ingress(
                    GroupId=security_group_idWS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]} ,
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                #print('depois')
                #print('Ingress Successfully Set %s' % data)
            except ClientError as e:
                #print('3')
                print(e)
            break
        k+=1
    if k == len(SG):
            try:
                responseDB = ec2.create_security_group(GroupName='APS_DelchDB',
                                                    Description='Security group do DataBase',
                                                    VpcId=vpc_id)
                responseWS = ec2.create_security_group(GroupName='APS_DelchWS',
                                                    Description='Security group do webServer',
                                                    VpcId=vpc_id)           
                security_group_idDB = responseDB['GroupId']
                security_group_idWS = responseWS['GroupId']
                data = ec2.authorize_security_group_ingress(                   
                    GroupId=security_group_idDB,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp':'{}/32'.format(WS['PublicIp'])}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2.authorize_security_group_ingress(
                    GroupId=security_group_idWS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]} ,
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                #print('depois')
                #print('Ingress Successfully Set %s' % data)
            except ClientError as e:
                #print('3')
                print(e)
    
    return [responseDB,responseWS]


ipDelete=[]
idDelete=[]
for i in instancia['Reservations']:
    for j in i['Instances']:
        idDelete.append(j['InstanceId'])
        for k in j['NetworkInterfaces']:
            ipDelete.append(k['Association']['PublicIp'])
if (len(idDelete)!= 0):

    response = ec2.terminate_instances(InstanceIds=idDelete)

    waiter = ec2.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=idDelete)

decribeIP=ec2.describe_addresses(PublicIps=ipDelete)

for i in decribeIP['Addresses']:
    response = ec2.release_address(AllocationId=i['AllocationId'])

allocationDB = ec2.allocate_address()
allocationWS = ec2.allocate_address()


KeyPair = geraKeyPair()
SecurityGroup = createSecurityGroup(allocationDB,allocationWS)
sgidDB=SecurityGroup[0]['GroupId']
sgidWS=SecurityGroup[1]['GroupId']
defaultSGid  = ec2.describe_security_groups(GroupNames=['default'])
defaultSGid = defaultSGid['SecurityGroups'][0]['GroupId']


user_data_scriptDB = '''#!/bin/bash
cd /home/ubuntu
git clone https://github.com/Veronur/DatabaseCloud.git
cd ../..
sudo sh /home/ubuntu/DatabaseCloud/comandos.sh
'''

DBIP=allocationDB['PublicIp']
user_data_WS='''#!/bin/bash
cd /home/ubuntu
git clone https://github.com/Veronur/DatabaseCloud.git
cd ../..
sudo sh /home/ubuntu/DatabaseCloud/comandosWS.sh
sudo nano /etc/rc.local
echo "#!/bin/sh -e" >> /etc/rc.local
echo "cd .." >> /etc/rc.local
echo "cd home/ubuntu/DatabaseCloud" >> /etc/rc.local
echo "python3 setup.py {0}" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod +x /etc/rc.local
python3 /home/ubuntu/DatabaseCloud/setup.py {1}
'''.format(DBIP,DBIP)

print(user_data_WS)

instanceWS = ec2.run_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='Aps3Delch',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgidWS,defaultSGid],
    UserData=user_data_WS,
    TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value':'Lucca Delchairo Costabile'
                },
                {
                    'Key': 'Name',
                    'Value':'WebServerDelch'
                }
            ]
        }   
    ])


instanceDB = ec2.run_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='Aps3Delch',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgidDB,defaultSGid],
    UserData=user_data_scriptDB,
    TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value':'Lucca Delchairo Costabile'
                },
                {
                    'Key': 'Name',
                    'Value':'DataBaseDelch'
                }
            ]
        }   
    ])

waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instanceDB['Instances'][0]['InstanceId'],instanceWS['Instances'][0]['InstanceId']])

try:    
    response = ec2.associate_address(AllocationId=allocationDB['AllocationId'],
                                     InstanceId=instanceDB['Instances'][0]['InstanceId'])
    #print(response)
except ClientError as e:
    print(e)


try:
    response = ec2.associate_address(AllocationId=allocationWS['AllocationId'],
                                     InstanceId=instanceWS['Instances'][0]['InstanceId'])
    #print(response)
except ClientError as e:
    print(e)

instancia = ec2.describe_instances(
    Filters=[
        {
            'Name': 'tag:Owner',
            'Values': ['Lucca Delchairo Costabile']
        }
    ]  
)
