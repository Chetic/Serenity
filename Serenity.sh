#!/bin/bash
 
while [ 1 ]; do
{
stdbuf -oL python /home/pi/Serenity/Serenity.py >/home/pi/Serenity/serenity.log
sleep 1
}
 
done
