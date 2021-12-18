for module in PA PAopt
do
  for repo in blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy
  do
    timeout 1800 time python3.9 -m da --message-buffer-size=409600000 --rule launcher.da --data data/$repo --module $module 1>>out.txt 2>>msg.txt
    echo "end $module-$repo" >>out.txt 
    echo "end $module-$repo" >>msg.txt

    for FILE in $(ls __pycache__/PA.*class_extends_rs*facts)
    do
      mv "$FILE" __pycache__/$repo.txt
    done
  done
done

for module in paxsb paoptxsb paxsb_manualopt
do
  for repo in blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy
  do
    timeout 1800 time xsb -e "[$module], load_dync('__pycache__/$repo.facts'), halt."  1>>xsb_out.txt 2>>xsb_msg.txt
    echo "end $module-$repo" >>xsb_out.txt
    echo "end $module-$repo" >>xsb_msg.txt
  done
done
