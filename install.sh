#!/bin/bash
main(){
  mkdir ./Crack
  cd ./Crack
  apt-get update
  apt-get install python3.7.6 -y
  wget -O Server.py https://raw.githubusercontent.com/breakwa2333/Crack/master/Server.py
  python3.7.6 Server.py
}
