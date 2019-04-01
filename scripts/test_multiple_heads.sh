lines=`python3 manage.py db heads | grep -c "head" | wc | awk '{print $1}'`
if [ $lines -ne 1 ]
then
    echo "Error: Multiple Migration Heads"
	exit 1
else
	exit 0
fi

