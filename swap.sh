#!/bin/bash

# Sécuriser les permissions
sudo chmod 600 /swapfile

# Formater le fichier en tant que swap
sudo mkswap /swapfile

# Activer le swap immédiatement
sudo swapon /swapfile

# Ajouter à /etc/fstab pour la persistance au redémarrage (si pas déjà présent)
if ! grep -q "/swapfile" /etc/fstab; then
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  echo "Swap ajouté à /etc/fstab."
else
  echo "Le swap est déjà configuré dans /etc/fstab."
fi

# Vérification
swapon --show
