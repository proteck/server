#!/bin/bash

start=`date +%s`

SEP = \n---------------------------

echo $SEP
echo Archives
rclone sync smb_syno:/home/Documents/Archives/ drive:_Save/syno/Archives/ --progress


echo $SEP
echo Autre
rclone sync smb_syno:/home/Documents/Autre/ drive:_Save/syno/Autre/ --progress

echo $SEP
echo Estivale
rclone sync smb_syno:/home/Documents/Estivale drive:_Save/syno/Estivale/ --progress

# echo $SEP
# echo Mobile Whatsapp
# rclone sync smb_syno:/home/Documents/Mobile\ Whatsapp/ drive:_Save/syno/Mobile\ Whatsapp/ --progress

# echo $SEP
# echo Mobile Whatsapp
# rclone sync smb_syno:/home/Documents/Mobile\ Whatsapp/ drive:_Save/syno/Mobile\ Whatsapp/ --progress

echo $SEP
echo Note
rclone sync smb_syno:/home/Documents/Note/ drive:_Save/syno/Note/ --progress

echo $SEP
echo Site web
rclone sync smb_syno:/home/Documents/Site\ web/ drive:_Save/syno/Site\ web/ --progress

echo $SEP
echo Tir à l\'arc
rclone sync smb_syno:/home/Documents/Tir\ à\ l\ arc/ drive:_Save/syno/Tir\ à\ l\ arc/ --progress

echo $SEP
echo MINIO
rclone copy minio:dokploy drive:_Save/rclone/ --progress

end=`date +%s`
runtime=$((end-start))
echo Runtime : $runtime
