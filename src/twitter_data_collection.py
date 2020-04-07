#
# I going to do a Twitter Data Collection in order to fetch Tweets
# and save them into a normalize dataset.
#

import twint

print('Hello World !!')


# Configure
c = twint.Config()
#c.Username = "sebaxtianbach"
c.Search = ["accidente", "movilidad"]
#c.Location = True
#c.Geo = "3.398547, -76.525841, 1km"
#c.Format = "ID {id} | Username {username} | Geo {geo} | Tweet {tweet} | Source {source}"
c.Near = "Cali"
c.Limit = 20
#c.Store_csv = True
#c.Output = "./src/output/accidentes.csv"
c.Lowercase = True
c.Images = True
c.Since = "2020-01-01"
c.Count = True
#c.Format = "ID {id} | Username {username} | Tweet {tweet} | Photos {photos}"

# Run
twint.run.Search(c)
