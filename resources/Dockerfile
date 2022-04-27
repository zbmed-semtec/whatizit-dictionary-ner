FROM tomcat:8-jre8

RUN \
  apt-get update && \
  apt-get -y install python3 && \
  apt-get -y clean && \
  rm -rf /var/lib/apt/lists/*

RUN \
  apt-get update && \
  apt-get install -y python3-pip && \
  pip3 install requests beautifulsoup4 && \
  pip3 install lxml

RUN \
  apt-get update && \
  apt-get install -y sudo && \
  useradd whatizit && echo "whatizit:whatizit" | chpasswd && adduser whatizit sudo

RUN \
  apt-get install -y nano && \
  apt-get install -y procps

ADD monq /home/whatizit/monq

RUN \
  chown whatizit /home/whatizit/monq -R && \
  chmod 777 /home/whatizit/monq -R 

ENV MONQ /home/whatizit/monq
ENV PATH ${MONQ}/bin:${PATH}
ENV MONQLIB ${MONQ}/lib
ENV CLASSPATH ${MONQLIB}/monq-1.0.jar:${MONQLIB}/indexing.jar:${MONQLIB}/xstream-1.4.7.jar:${MONQLIB}/ie.jar:${MONQLIB}/marie.jar:${MONQLIB}/retrieval.jar:${MONQLIB}/citationfinder.jar
  
ADD script.sh /script/script.sh

RUN chmod 777 /script/script.sh 

CMD ["/bin/bash", "-c", "/script/script.sh"]
