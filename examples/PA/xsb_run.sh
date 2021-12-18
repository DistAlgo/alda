for module in paxsb paoptxsb paxsb_manualopt
do
  for repo in blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy
  do
    timeout 1800 time xsb -e "[$module], load_dync('__pycache__/$repo.facts'), halt."  1>>xsb_out.txt 2>>xsb_msg.txt
    echo "end $module-$repo" >>xsb_out.txt
    echo "end $module-$repo" >>xsb_msg.txt
  done
done
