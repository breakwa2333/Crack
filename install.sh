#!/bin/bash
service(){
  touch ./Crack/Crack.service
  cat>./Crack/Crack.service<<EOF
  [Unit]
  Description=test deamon
  After=rc-local.service

  [Service]
  Type=simple
  User=root
  Group=root
  WorkingDirectory=$(cd "$(dirname "$0")";pwd)/Crack
  ExecStart=/usr/bin/python3 $(cd "$(dirname "$0")";pwd)/Crack/server.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
EOF
}

main(){
  mkdir ./Crack
  cd ./Crack
  apt-get update
  apt-get install python3.7.6 -y
  wget -O Server.py https://raw.githubusercontent.com/breakwa2333/Crack/master/Server.py
  service
  mv ./Crack/Crack.service /etc/systemd/system/
  systemctl enable Crack.service
  systemctl start Crack.service
}

main
