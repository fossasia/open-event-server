lines=`python manage.py db heads | wc | awk '{print $1}'`
if [ $lines -ne 1 ]
then
	exit 1
else
	exit 0
fi

