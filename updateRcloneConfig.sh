#!/bin/sh

cp /home/maxime/.config/rclone/rclone.conf rclone.conf

cat rclone.conf | base64 > rclone_b64.txt
rm rclone.conf
