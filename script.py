import os
import boto3
from botocore.exceptions import ClientError
import time

ec2_1 = boto3.client('ec2',region_name='us-east-1')
ec2_2 = boto3.client('ec2',region_name='us-east-2')

instancia_1 = ec2_1.describe_instances(
    Filters=[
        {
            'Name': 'tag:Owner',
            'Values': ['Lucca Delchairo Costabile']
        }
    ]  
)

instancia_2 = ec2_2.describe_instances(
    Filters=[
        {
            'Name': 'tag:Owner',
            'Values': ['Lucca Delchairo Costabile']
        }
    ]  
)



def geraKeyPair():
    chaves1 = ec2_1.describe_key_pairs()['KeyPairs']
    k=0
    for i in chaves1: 
        if i['KeyName']=="ProgDelch_1":
            response1 = ec2_1.delete_key_pair(KeyName='ProgDelch_1')
            response1 = ec2_1.create_key_pair(KeyName='ProgDelch_1') 
            f= open("ProgDelch_1.pem","w+")
            f.write(response1['KeyMaterial'])
            f.close()
            os.chmod("ProgDelch_1.pem", 400)
            break
        k+=1
    if k == len(chaves1):
        response1 = ec2_1.create_key_pair(KeyName='ProgDelch_1')
        f= open("ProgDelch_1.pem","w+")
        f.write(response1['KeyMaterial'])
        f.close()
        os.chmod("ProgDelch_1.pem", 400)
        #os.chow("ProgDelch_1.pem")


    chaves2 = ec2_2.describe_key_pairs()['KeyPairs']
    k=0
    for i in chaves2: 
        if i['KeyName']=="ProgDelch_2":
            response2 = ec2_2.delete_key_pair(KeyName='ProgDelch_2')
            response2 = ec2_2.create_key_pair(KeyName='ProgDelch_2') 
            f= open("ProgDelch_2.pem","w+")
            f.write(response2['KeyMaterial'])
            f.close()
            os.chmod("ProgDelch_2.pem", 400)
            break
        k+=1
    if k == len(chaves2):
        response2 = ec2_2.create_key_pair(KeyName='ProgDelch_2')
        f= open("ProgDelch_2.pem","w+")
        f.write(response2['KeyMaterial'])
        f.close()
        os.chmod("ProgDelch_2.pem", 400)    
    return [response1, response2]

def createSecurityGroup(Redirect,WS):
    
    #_____US-East-1_____#

    response_1 = ec2_1.describe_vpcs()
    vpc_id = response_1.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        SG_1 = ec2_1.describe_security_groups()['SecurityGroups']
        #print(response)
    except ClientError as e:
        #print('2')
        print(e)

    k=0
    for i in SG_1: 
        if i['GroupName']=='Projeto_Delch' or i['GroupName']=='Projeto_DelchRed':
            try:
                responseAS = ec2_1.delete_security_group(GroupName='Projeto_Delch')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)  
            try:
                responseR = ec2_1.delete_security_group(GroupName='Projeto_DelchRed')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)  
                
            try:
                responseAS = ec2_1.create_security_group(GroupName='Projeto_Delch',
                                                    Description='Security group da AutoScaling',
                                                    VpcId=vpc_id)
                responseR = ec2_1.create_security_group(GroupName='Projeto_DelchRed',
                                                    Description='Security group do Redirect',
                                                    VpcId=vpc_id)
                security_group_idAS = responseAS['GroupId']
                security_group_idR = responseR['GroupId']
                #print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
                #print('antes')
                data = ec2_1.authorize_security_group_ingress(
                    GroupId=security_group_idR,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2_1.authorize_security_group_ingress(
                    GroupId=security_group_idAS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
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

    if k == len(SG_1):
            try:
                responseAS = ec2_1.create_security_group(GroupName='Projeto_Delch',
                                                    Description='Security group da AutoScaling',
                                                    VpcId=vpc_id)
                responseR = ec2_1.create_security_group(GroupName='Projeto_DelchRed',
                                                    Description='Security group do Redirect',
                                                    VpcId=vpc_id)
                security_group_idAS = responseAS['GroupId']
                security_group_idR = responseR['GroupId']
                #print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
                #print('antes')
                data = ec2_1.authorize_security_group_ingress(
                    GroupId=security_group_idR,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp':'{}/32'.format(Redirect['PublicIp'])}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2_1.authorize_security_group_ingress(
                    GroupId=security_group_idAS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
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
    
    #______US-East-2______#
    response_2 = ec2_2.describe_vpcs()
    vpc_id = response_2.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        SG_2 = ec2_2.describe_security_groups()['SecurityGroups']
        #print(response)
    except ClientError as e:
        #print('2')
        print(e)
    k=0
    for i in SG_2: 
        if i['GroupName']=='DelchDB' or i['GroupName']=='DelchWS':
            try:
                response_2 = ec2_2.delete_security_group(GroupName='DelchDB')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)
            try:
                response_2 = ec2_2.delete_security_group(GroupName='DelchWS')
                #print('Security Group Deleted')
            except ClientError as e:
                #print("1")
                print(e)        
            try:
                responseDB = ec2_2.create_security_group(GroupName='DelchDB',
                                                    Description='Security group do DataBase',
                                                    VpcId=vpc_id)
                responseWS = ec2_2.create_security_group(GroupName='DelchWS',
                                                    Description='Security group do webServer',
                                                    VpcId=vpc_id)           
                security_group_idDB = responseDB['GroupId']
                security_group_idWS = responseWS['GroupId']
                data = ec2_2.authorize_security_group_ingress(
                    GroupId=security_group_idDB,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 3306,
                        'ToPort': 3306,
                        'IpRanges': [{'CidrIp':'{}/32'.format(WS['PublicIp'])}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2_2.authorize_security_group_ingress(
                    GroupId=security_group_idWS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp':'{}/32'.format(Redirect['PublicIp'])}]} ,
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
    if k == len(SG_2):
            try:
                responseDB = ec2_2.create_security_group(GroupName='DelchDB',
                                                    Description='Security group do DataBase',
                                                    VpcId=vpc_id)
                responseWS = ec2_2.create_security_group(GroupName='DelchWS',
                                                    Description='Security group do webServer',
                                                    VpcId=vpc_id)           
                security_group_idDB = responseDB['GroupId']
                security_group_idWS = responseWS['GroupId']
                data = ec2_2.authorize_security_group_ingress(
                    GroupId=security_group_idDB,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 3306,
                        'ToPort': 3306,
                        'IpRanges': [{'CidrIp':'{}/32'.format(WS['PublicIp'])}]},  
                        {'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}                     
                    ])
                data = ec2_2.authorize_security_group_ingress(
                    GroupId=security_group_idWS,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp':'{}/32'.format(Redirect['PublicIp'])}]} ,
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
    
    return [responseAS, responseR, responseDB,responseWS]

ipDelete_1=[]
idDelete_1=[]
ipDelete_2=[]
idDelete_2=[]

for i in instancia_1['Reservations']:
    for j in i['Instances']:
        idDelete_1.append(j['InstanceId'])
        for k in j['NetworkInterfaces']:
            ipDelete_1.append(k['Association']['PublicIp'])
for i in instancia_2['Reservations']:
    for j in i['Instances']:
        idDelete_2.append(j['InstanceId'])
        for k in j['NetworkInterfaces']:
            ipDelete_2.append(k['Association']['PublicIp'])

if (len(idDelete_1)!= 0):
    response = ec2_1.terminate_instances(InstanceIds=idDelete_1)
    waiter = ec2_1.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=idDelete_1)


if (len(idDelete_2)!= 0):

    response = ec2_2.terminate_instances(InstanceIds=idDelete_2)

    waiter = ec2_2.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=idDelete_2)



decribeIP_1=[]
for i in ipDelete_1:
    try:
        decribeIP_1.append(ec2_1.describe_addresses(PublicIps=[i]))
    except ClientError as e:
        #print(e)
        pass


for i in decribeIP_1:
    for j in i['Addresses']:
        try:
            response = ec2_1.release_address(AllocationId=j['AllocationId'])
        except ClientError as e:
            print(e)
            pass

#print(response)

decribeIP_2=[]
try:
    decribeIP_2=ec2_2.describe_addresses(PublicIps=ipDelete_2)
except ClientError as e:
    print(e)

try:
    for i in decribeIP_2['Addresses']:
        try:
            response = ec2_2.release_address(AllocationId=i['AllocationId'])
        except ClientError as e:
            print(e)
except ClientError as e:
    print(e)

allocationR = ec2_1.allocate_address()
allocationDB = ec2_2.allocate_address()
allocationWS = ec2_2.allocate_address()

lB= boto3.client('elbv2')
aS = boto3.client('autoscaling')

flag=True
flag2=True
try:
    response = aS.suspend_processes(AutoScalingGroupName='AutoScaleDelchProjeto')
except:
    pass
while(True):
    #Deleta Listener e Load Balancer
    if flag:
        try:
            ARN = lB.describe_load_balancers(Names=['LoadBalancerProjetoDelch'])
            ARN = ARN['LoadBalancers'][0]['LoadBalancerArn']
            ARNL = lB.describe_listeners(LoadBalancerArn=ARN)
            ARNL = ARNL['Listeners'][0]['ListenerArn']
            ARNTG = response = client.describe_target_groups(LoadBalancerArn=ARN)
            ARNTG = ARNTG['TargetGroups'][0]['TargetGroupArn']
            flag = False
        except:
            pass

    try:
        response = lB.delete_listener(ListenerArn=ARNL)
    except:
        pass

    try:    
        response = lB.delete_load_balancer(LoadBalancerArn=ARN)
        waiter = lB.get_waiter('load_balancers_deleted')
        waiter.wait(LoadBalancerArns=ARN)
    except:
        pass


    #Deleta AutoScalingGroup
    try:
        response = aS.delete_auto_scaling_group(AutoScalingGroupName='AutoScaleDelchProjeto',ForceDelete=True)
    except ClientError as e:
        #print(e)
        pass
    #Deleta Launch Configuration 
    try:
        response = aS.delete_launch_configuration(LaunchConfigurationName='LaunchConfDelch')  
    except:
        pass
    try:
        response = lB.delete_target_group(TargetGroupArn=ARNTG)
    except:
        pass
    #Prende o codigo ate que tudo seja realmente deletado
    check = aS.describe_auto_scaling_groups(AutoScalingGroupNames=['AutoScaleDelchProjeto'])
    if (len(check['AutoScalingGroups'])==0):     
        check2 = aS.describe_launch_configurations(LaunchConfigurationNames=['LaunchConfDelch'])
        if (len(check2['LaunchConfigurations'])==0):         
            break

print("\nAmbiente pronto")
KeyPair = geraKeyPair()
SecurityGroup = createSecurityGroup(allocationR,allocationWS)

sgid=SecurityGroup[0]['GroupId']
sgidR=SecurityGroup[1]['GroupId']
sgidDB=SecurityGroup[2]['GroupId']
sgidWS=SecurityGroup[3]['GroupId']

defaultSGid_1  = ec2_1.describe_security_groups(GroupNames=['default'])
defaultSGid_1 = defaultSGid_1['SecurityGroups'][0]['GroupId']
defaultSGid_2  = ec2_2.describe_security_groups(GroupNames=['default'])
defaultSGid_2 = defaultSGid_2['SecurityGroups'][0]['GroupId']

user_data_script = '''#!/bin/bash
cd /home/ubuntu
git clone https://github.com/Veronur/APS1Coud.git
cd ../..
sudo sh /home/ubuntu/APS1Coud/comandos.sh
sudo nano /etc/rc.local
echo "#!/bin/sh -e" >> /etc/rc.local
echo "cd .." >> /etc/rc.local
echo "cd home/ubuntu/APS1Coud" >> /etc/rc.local
echo "python3 server.py {}" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod +x /etc/rc.local
sudo reboot'''.format(allocationR['PublicIp'])

user_data_scriptR = '''#!/bin/bash
cd /home/ubuntu
git clone https://github.com/Veronur/APS1Coud.git
cd ../..
sudo sh /home/ubuntu/APS1Coud/comandos.sh
sudo nano /etc/rc.local
echo "#!/bin/sh -e" >> /etc/rc.local
echo "cd .." >> /etc/rc.local
echo "cd home/ubuntu/APS1Coud" >> /etc/rc.local
echo "python3 server.py {}" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod +x /etc/rc.local
sudo reboot'''.format(allocationWS['PublicIp'])

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

instanceR = ec2_1.run_instances(
    ImageId='ami-04b9e92b5572fa0d1',
    InstanceType='t2.micro',
    KeyName='ProgDelch_1',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgidR,defaultSGid_1],
    UserData=user_data_scriptR,
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
                    'Value':'RedirectDelch'
                }
            ]
        }   
    ])

instanceWS = ec2_2.run_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='ProgDelch_2',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgidWS,defaultSGid_2],
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


instanceDB = ec2_2.run_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='ProgDelch_2',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgidDB,defaultSGid_2],
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

waiter = ec2_2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instanceDB['Instances'][0]['InstanceId'],instanceWS['Instances'][0]['InstanceId']])
waiter = ec2_1.get_waiter('instance_running')
waiter.wait(InstanceIds=[instanceR['Instances'][0]['InstanceId']])

try:    
    response = ec2_1.associate_address(AllocationId=allocationR['AllocationId'],
                                     InstanceId=instanceR['Instances'][0]['InstanceId'])
    #print(response)
except ClientError as e:
    print(e)

try:    
    response = ec2_2.associate_address(AllocationId=allocationDB['AllocationId'],
                                     InstanceId=instanceDB['Instances'][0]['InstanceId'])
    #print(response)
except ClientError as e:
    print(e)


try:
    response = ec2_2.associate_address(AllocationId=allocationWS['AllocationId'],
                                     InstanceId=instanceWS['Instances'][0]['InstanceId'])
    #print(response)
except ClientError as e:
    print(e)



instance = ec2_1.run_instances(
    ImageId='ami-04b9e92b5572fa0d1',
    InstanceType='t2.micro',
    KeyName='ProgDelch_1',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[sgid,defaultSGid_1],
    UserData=user_data_script,
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
                    'Value':'PROJETO_DELCH'
                }
            ]
        }   
    ])

##Cria a intancia para o launch Configuration, usa a imagem dela, e depois a deleta##
idCreate=instance['Instances'][0]['InstanceId']
waiter = ec2_1.get_waiter('instance_running')
waiter.wait(InstanceIds=[idCreate])
print("\nIntancia modelo criada")
launchConf = aS.create_launch_configuration(
    LaunchConfigurationName='LaunchConfDelch',
    KeyName='ProgDelch_1',
    SecurityGroups=[sgid,defaultSGid_1],
    UserData=user_data_script,
    InstanceId=idCreate
)
response = ec2_1.terminate_instances(InstanceIds=[idCreate])
print("\nLaunch Configuration criada")
waiter = ec2_1.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[idCreate])
print("\nIntancia modelo deletada")
##_________________________________________________________________________________##

response = ec2_1.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
TargetGroup = lB.create_target_group(
    Name='TGProjetoDelch',
    Protocol='HTTP',
    VpcId=vpc_id,
    Port=5000,
    TargetType='instance'
)

subnets = ec2_1.describe_subnets(
    Filters=[
        {
            'Name': 'availabilityZone',
            'Values': [
                'us-east-1a',
                'us-east-1b',
                'us-east-1c',
                'us-east-1d',
                'us-east-1e',
                'us-east-1f',
            ]
        }
    ]
)
SN=[]
for i in subnets['Subnets']:
    SN.append(i['SubnetId'])
loadBalance=lB.create_load_balancer(
    Name='LoadBalancerProjetoDelch',        
    Subnets=SN,
    SecurityGroups=[sgid,defaultSGid_1],
    Scheme='internet-facing',   
    Type='application',
    IpAddressType='ipv4'
)

print('\nEsperando load Balancer ficar pronto')
waiter = lB.get_waiter('load_balancer_available')
waiter.wait(Names=['LoadBalancerProjetoDelch'])

listener = lB.create_listener(
    LoadBalancerArn=loadBalance['LoadBalancers'][0]['LoadBalancerArn'],
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn':TargetGroup['TargetGroups'][0]['TargetGroupArn']
        }
    ]
)


autoScale = aS.create_auto_scaling_group(
    AutoScalingGroupName='AutoScaleDelchProjeto',
    LaunchConfigurationName='LaunchConfDelch',
    AvailabilityZones=[
        'us-east-1a',
        'us-east-1b',
        'us-east-1c',
        'us-east-1d',
        'us-east-1e',
        'us-east-1f'
    ],
    TargetGroupARNs=[TargetGroup['TargetGroups'][0]['TargetGroupArn']],
    MinSize=1,
    MaxSize=5,
    Tags=[
        {
            'ResourceId': 'AutoScaleDelchProjeto',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Owner',
            'Value': 'Lucca Delchairo Costabile',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'AutoScaleDelchProjeto',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Name',
            'Value': 'PROJETO_DELCH',
            'PropagateAtLaunch': True
        } 
    ]
)

print('DONE!')