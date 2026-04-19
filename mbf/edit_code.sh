#!/bin/sh

rclone copyto mbf:payments/payments.csv ./out.csv -v

code --wait out.csv

rclone moveto ./out.csv mbf:payments/payments.csv -v

echo "OK"

rclone lsf mbf:payments
echo "---"
rclone cat mbf:payments/payments.csv
