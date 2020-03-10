#
# I going to do a Twitter Data Collection in order to fetch Tweets
# and save them into a normalize dataset.
#

import twint

print('Hello World !!')


# Configure
c = twint.Config()
c.Username = "sebaxtianbach"
#c.Search = ["accidente"]
c.Location = True
#c.Geo = "3.449599, -76.544300, 1km"
#c.Format = "ID {id} | Username {username} | Geo {geo} | Tweet {tweet} | Source {source}"
#c.Near = "Cali"

# Run
twint.run.Search(c)
