#!/bin/bash

cd ~/deploy
. activate LAMSON
cd postosaurus/
rm run/smtp.pid
run/smtp.pid.lock 
rm run/log.pid
rm run/log.pid.lock 
ls run/
rm run/zeus.MainThread-*
lamson log
lamson start
cd scripts/
./ttservctl start

