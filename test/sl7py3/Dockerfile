FROM sl:7

RUN yum install -y git

RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh > miniconda.sh
RUN bash miniconda.sh -b -p /root/miniconda
RUN printf ". /root/miniconda/bin/activate\nexport nodoc=true\n" >> /root/.bashrc
