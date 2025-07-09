from flask import Blueprint, render_template

from security_check.aws_cloud.ec2 import AWSProfiles

profile_bp = Blueprint("aws_account_ids", __name__, url_prefix="/")


@profile_bp.route("", methods=["GET"])
def profile_list():
    profiles_info = AWSProfiles().get_profiles_info()
    return render_template("profiles.html", profiles_info=profiles_info)
