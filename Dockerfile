# This docker container acts as a runner for dagger. 
# Every time dagger calls on this Dockerfile it is built and used for the one use case.
FROM --platform=linux/x86_64 amazonlinux:latest

ARG tfv=1.3.1

# Install required repos
RUN : \
    && yum update -y \
    && yum install -y yum-utils \
    && yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo \
    && :

# Install required packages
RUN : \
    && yum install -y \
        terraform-${tfv} \
        jq \
        unzip \
        sudo \
        docker \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && :

# install aws cli https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
RUN : \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo ./aws/install \
    && rm -rf awscliv2.zip \
    && :

RUN : \
    && adduser circleci --uid 1500 --create-home --user-group \
    && :

RUN : \
    && mkdir -p /src \
    && chmod -R 777 /src \
    && mkdir -p /home/circleci/.aws \
    && chmod -R 777 /home/circleci \
    && :

USER circleci
