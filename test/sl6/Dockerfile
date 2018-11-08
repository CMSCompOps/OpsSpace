FROM sl:6

RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm

RUN yum -y install \
    python-pip \
    python-devel \
    git perl

RUN pip install -U 'pip==9.0.1'
