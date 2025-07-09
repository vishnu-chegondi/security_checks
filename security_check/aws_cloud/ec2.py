import boto3
import logging


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls.factory_holder = dict()
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AWSProfiles:
    def __init__(self):
        self.profiles = []
        for profile in boto3.session.Session().available_profiles:
            self.profiles.append(profile)

    def get_profiles_info(self):
        profiles_info = []
        for profile in self.profiles:
            try:
                session = boto3.Session(profile_name=profile)
                identity = session.client("sts").get_caller_identity()
                profiles_info.append(
                    {
                        "name": profile,
                        "account_id": identity["Account"],
                        "region": session.region_name,
                        "role": identity["Arn"].split("/")[1],
                        "user_id": identity["UserId"],
                    }
                )
            except Exception as e:
                logging.error(f"Error getting profile info for {profile}: {e}")
                continue
        return profiles_info

    def get_valid_profiles(self):
        valid_profiles = []
        for profile in self.profiles:
            try:
                session = boto3.Session(profile_name=profile)
                _ = session.client("sts").get_caller_identity()
                valid_profiles.append(profile)
            except Exception as e:
                logging.error(f"Error getting profile info for {profile}: {e}")
                continue
        return valid_profiles


class AWSSecurityCheckEC2:
    def __init__(self, aws_account_id):
        self.aws_account_id = aws_account_id
        self.session = boto3.Session(profile_name=self.aws_account_id)
        self.ec2 = self.session.client("ec2")
        self.instances = self.get_ec2_instances()

    def refresh_details(self, aws_account_id):
        self.instances = self.get_ec2_instances()

    def get_ec2_instances(self):
        instances = []
        response = self.ec2.describe_instances()
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instances.append(self.get_instance_details(instance))
        return instances

    def get_instance_details(self, instance):
        return dict(
            instance_id=instance["InstanceId"],
            instance_type=instance["InstanceType"],
            instance_state=instance["State"]["Name"],
            instance_launch_time=instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S"),
            instance_architecture=instance["Architecture"],
            instance_vpc_id=instance["VpcId"],
            instance_subnet_id=instance["SubnetId"],
            web_url=f"https://console.aws.amazon.com/ec2/v2/home?region={self.session.region_name}#Instances:instanceId={instance['InstanceId']}",
            instance_account_id=self.aws_account_id,
            metadata_options=instance["MetadataOptions"],
        )

    def get_count_imdsv1_instances(self):
        number_of_instances = 0
        imdsv1_instances = self.get_details_imdsv1_instances()
        for _ in imdsv1_instances:
            number_of_instances += 1
        return number_of_instances

    def get_details_imdsv1_instances(self):
        imdsv1_instances = []
        for instance in self.instances:
            logging.info(f"Checking instance {instance['instance_id']}")
            metadata = instance["metadata_options"]
            if metadata["HttpTokens"] == "optional":
                imdsv1_instances.append(instance)
        return imdsv1_instances


class AWSSecurityCheckFactory(metaclass=Singleton):

    def get_security_check(self, aws_account_id) -> AWSSecurityCheckEC2:
        if aws_account_id not in self.factory_holder:
            self.factory_holder[aws_account_id] = AWSSecurityCheckEC2(aws_account_id)
        self.factory_holder[aws_account_id].refresh_details(aws_account_id)
        return self.factory_holder[aws_account_id]
