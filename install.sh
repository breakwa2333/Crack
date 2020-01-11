#!/bin/bash
service(){
  touch $(cd "$(dirname "$0")";pwd)/Crack.service
  cat>$(cd "$(dirname "$0")";pwd)/Crack.service<<EOF
  [Unit]
  Description=test deamon
  After=rc-local.service

  [Service]
  Type=simple
  User=root
  Group=root
  WorkingDirectory=$(cd "$(dirname "$0")";pwd)
  ExecStart=/usr/bin/python3.7 $(cd "$(dirname "$0")";pwd)/Server.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
EOF
}

conf(){
  echo "alias Crack='vim $(cd "$(dirname "$0")";pwd)/crack_server.conf'">>~/.bashrc
  sleep 2
  source ~/.bashrc
}

debconf(){
  debconf-set-selections <<< "libssl1.1/restart-services Yes"
  debconf-set-selections <<< "libssl1.1/restart-failed Yes"
}

main(){
  mkdir $(cd "$(dirname "$0")";pwd)/Crack
  cd $(cd "$(dirname "$0")";pwd)/Crack
  apt-get update
  debconf
  apt-get install python3.7 -y
  wget -O Server.py https://raw.githubusercontent.com/breakwa2333/Crack/master/Server.py
  service
  mv $(cd "$(dirname "$0")";pwd)/Crack.service /etc/systemd/system/
  systemctl enable Crack.service
  systemctl start Crack.service
  conf
}

main
