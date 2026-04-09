for f in *.sh; do
  # On saute le fichier s'il commence par un underscore
  [[ "$f" == _* ]] && continue

  echo "------------------------------------------"
  echo "🚀 Lancement de : $f"
  echo "------------------------------------------"
  
  bash "$f"

  echo 
done
