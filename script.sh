#!/bin/bash
cd ${MONQ}/config && \
  hostnamevar=$(hostname) && \
  sed -i "s/<host>.*</<host>$hostnamevar</" *.svr && \
  cd ${MONQ}/bin && \
  echo y | ./startServer xmlElem && \
  echo y | ./startServer plainText && \
  echo cancer | DistFilter svr=plainText | head && \
  /usr/local/tomcat/bin/catalina.sh run
