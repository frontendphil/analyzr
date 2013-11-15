#!/bin/sh -f

CURRENT_DIR=$PWD

if [ ! -d "$CURRENT_DIR/../css" ]
then
    mkdir $CURRENT_DIR/../css
fi

for f in *.less
do
    file=$(basename $f)

    echo "Procsssing $file..."

    target=$(echo "$file" | sed -e "s/.less/.css/g")

    lessc "$file" > "$CURRENT_DIR/../css/$target"
done
