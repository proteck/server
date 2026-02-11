#!/bin/bash

start=`date +%s`

SEP = \n---------------------------

echo $SEP
echo Archives
rclone sync smb_syno:/home/Documents/Archives/ drive:_Save/syno/Archives/ --progress --verbose

echo $SEP
echo Autre
rclone sync smb_syno:/home/Documents/Autre/ drive:_Save/syno/Autre/ --progress --verbose

echo $SEP
echo Estivale
rclone sync smb_syno:/home/Documents/Estivale drive:_Save/syno/Estivale/ --progress --verbose

# echo $SEP
# echo Mobile Picture
# rclone sync smb_syno:/home/Documents/Mobile\ Picture/ drive:_Save/syno/Mobile\ Picture/ --progress --verbose

# echo $SEP
# echo Mobile Whatsapp
# rclone sync smb_syno:/home/Documents/Mobile\ Whatsapp/ drive:_Save/syno/Mobile\ Whatsapp/ --progress --verbose

echo $SEP
echo Note
rclone sync smb_syno:/home/Documents/Note/ drive:_Save/syno/Note/ --progress --verbose

# echo $SEP
# echo Photos
# rclone sync smb_syno:/home/Documents/Photos/ drive:_Save/syno/Photos/ --progress --verbose

echo $SEP
echo Site web
rclone sync smb_syno:/home/Documents/Site\ web/ drive:_Save/syno/Site\ web/ --progress --verbose

echo $SEP
echo Tir à l\'arc
rclone sync smb_syno:/home/Documents/Tir\ à\ l\ arc/ drive:_Save/syno/Tir\ à\ l\ arc/ --progress --verbose

echo $SEP
echo MINIO
rclone copy minio:dokploy drive:_Save/rclone/ --progress --verbose

echo $SEP

end=`date +%s`
runtime=$((end-start))
echo Runtime : $runtime secondes
