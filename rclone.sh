#!/bin/bash

echo Autre
rclone sync smb_syno:/home/Documents/Autre/ drive:_Save/syno/Autre/ --progress

echo Estivale
rclone sync smb_syno:/home/Documents/Estivale drive:_Save/syno/Estivale/ --progress

# echo Mobile Whatsapp
# rclone sync smb_syno:/home/Documents/Mobile\ Whatsapp/ drive:_Save/syno/Mobile\ Whatsapp/ --progress

echo Note
rclone sync smb_syno:/home/Documents/Note/ drive:_Save/syno/Note/ --progress

echo Site web
rclone sync smb_syno:/home/Documents/Site web/ drive:_Save/syno/Site web/ --progress

echo Tir à l\'arc
rclone sync smb_syno:/home/Documents/Tir à l arc/ drive:_Save/syno/Tir à l arc/ --progress

echo ------------------

echo MINIO
rclone sync minio:dokploy drive:_Save/rclone/ --progress
