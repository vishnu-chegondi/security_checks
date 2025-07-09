from flask import Blueprint, request, render_template
from security_check.aws_cloud.ec2 import (
    AWSSecurityCheckFactory,
    AWSSecurityCheckEC2,
    AWSProfiles,
)

aws_bp = Blueprint("aws_security_checks", __name__, url_prefix="/aws")


@aws_bp.route("/ec2", methods=["GET"], defaults={"aws_account_id": None})
@aws_bp.route("ec2/<aws_account_id>", methods=["GET"])
def security_check_list(aws_account_id):
    profiles = AWSProfiles().get_valid_profiles()
    checks = []
    if aws_account_id is None:
        return render_template("dashboard.html", checks=checks, profiles=profiles)
    aws_security_check = AWSSecurityCheckFactory().get_security_check(aws_account_id)
    imdsv1_instance_count = aws_security_check.get_count_imdsv1_instances()
    total_instance_count = len(aws_security_check.instances)
    checks.append(
        {
            "name": "IMDSv1",
            "description": "Instance Metadata Service can be accessed without authentication. We need to migrate to IMDSv2.",
            "imdsv1_count": imdsv1_instance_count,
            "total_count": total_instance_count,
            "url": f"/ec2/imdsv1/{aws_account_id}",
            "aws_account_id": aws_account_id,
        }
    )
    return render_template(
        "dashboard.html",
        checks=checks,
        aws_account_id=aws_account_id,
        profiles=profiles,
    )


@aws_bp.route("/ec2/imdsv1/<aws_account_id>", methods=["GET"])
def security_check_imdsv1(aws_account_id):
    aws_security_check = AWSSecurityCheckFactory().get_security_check(aws_account_id)
    imdsv1_instances = aws_security_check.get_details_imdsv1_instances()
    profiles = AWSProfiles().get_valid_profiles()
    return render_template(
        "instances.html",
        instances=imdsv1_instances,
        aws_account_id=aws_account_id,
        profiles=profiles,
    )
