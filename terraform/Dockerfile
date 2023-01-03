FROM --platform=linux/x86_64 amazonlinux:latest

ARG tfv=1.3.1

# update security
RUN : \
    && yum -y update --security \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && :

# Install required packages
RUN : \
    && yum update -y \
    && yum install -y yum-utils \
    && yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo \
    && yum install -y \
        terraform-${tfv} \
        jq \
        docker \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && :

RUN : \
    && mkdir -p /src \
    && chmod -R 777 /src \
    && :
