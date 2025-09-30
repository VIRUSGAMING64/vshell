id='1'
pip install -r requirements.txt --break-system-packages --timeout 5000
echo 'CRAETING DIRECTORIES'
mkdir bots
mkdir bots/sub_$id
cp -r modules ./bots/sub_$id/modules
cp -r web ./bots/sub_$id/web
cp -r templates ./bots/sub_$id/templates
cp bot.py ./bots/sub_$id/bot.py
echo 'FINISHIED'
echo 'RUNNING BOT'
python bots/sub_$id/bot.py