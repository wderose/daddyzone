1. Install Python 3.7.4 (https://www.python.org/downloads/release/python-374/)
2. Open Terminal.app and run `which python3`. Should point to what was just installed.
3. Install `pip` and then `pip install virtualenv`
4. `virtualenv -p python3 $HOME/envs/daddyzone`
5. `source ~/envs/daddyzone/bin/activate`
6. `pip install -r requirements.txt`
7.  `cd daddyzone && unset PYTHONPATH && scrapy crawl transactions`
