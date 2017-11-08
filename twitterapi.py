import twitter

retweet_id = 850439061273804801
retweet_link = "https://twitter.com/SilverVVulpes/status/850439061273804801"

api = twitter.Api(
	access_token_key="2316030886-3Dqq9g7AqOEeG8afE4aXE9rPs9EWQ4VJzn0BEP3",
	access_token_secret="u6Pn3Js8MHMzfu08uhBzamO83J65rffyEIm6AYWH8OUsz",
	consumer_key="vqmHOBNHTNPP7KGJ0sMLp4sRT",
	consumer_secret="o0wTMD0kxWLdbuEBZUg5w6KDr1ypTy0k3z2xt8V11pND5xJvNN",
	)

def getLastStatusByUsername(username):
	statuses = api.GetUserTimeline(screen_name=username)
	return (statuses[0])

def isLastStatusOurRepost(status):
	try:
		return status.retweeted_status.id == retweet_id
	except:
		return False

def doesUserExist(username):
	try:
		api.GetUser(screen_name=username)
		return True
	except:
		return False

#status = getLastStatusByUsername("thetimujin")
#print (isLastStatusOurRepost(status))
