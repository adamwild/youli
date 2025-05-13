def get_latest_post(username, password):
    import praw
    from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_USER_AGENT

    PASSWORD = password

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=PASSWORD,
        user_agent=REDDIT_USER_AGENT
    )

    # Fetch the latest submission by the target user
    def get_latest_post(username):
        redditor = reddit.redditor(username)
        latest = next(redditor.submissions.new(limit=1), None)

        if latest:
            return latest.title, latest.permalink
        else:
            return "", ""

    title, permalink = get_latest_post(username)
    return title, permalink

if __name__ == '__main__':
    # The user you want to track
    username = "Basilisk_Research"
    get_latest_post(username)