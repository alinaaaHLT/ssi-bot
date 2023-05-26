import praw
import json

# you need to edit the values below, obviously
reddit = praw.Reddit(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
    password="PASSWORD",
    user_agent="AGENT",
    username="USERNAME",
)

# enter the subreddits you want to scrape from
sub_names = ['all']

def walk2top(comment_obj):
    post_obj = comment_obj.submission
    tagged_replies = ""
    current_obj = comment_obj.parent() # don't include comment in prompt
    level = 0
    while not isinstance(current_obj, praw.models.Submission): # recurse until you reach the submission
        comment_text = current_obj.body.encode('ascii', 'ignore').decode()
        if current_obj.author == post_obj.author:
            tagged_reply = f"<|soopr|>{comment_text}<|eoopr|>"
        else:
            tagged_reply = f"<|sor|>{comment_text}<|eor|>"
        tagged_replies = tagged_reply + tagged_replies
        current_obj = current_obj.parent()
        level += 1
        if level>6: # don't include comment threads longer than 3 turns
            at_top = False
            break
    post_title = post_obj.title.encode('ascii', 'ignore').decode()
    tagged_title = f"<|sot|>{post_title}<|eot|>"
    if post_obj.is_self:
        post_text = post_obj.selftext.encode('ascii', 'ignore').decode()
        tagged_string = f"<|soss|>{tagged_title}<|sost|>{post_text}<|eost|>{tagged_replies}"
    else:
        tagged_string = f"<|sols|>{tagged_title}<|sol|>{post_obj.url}<|eol|>{tagged_replies}"
    return tagged_string

scraped_data = open('scraped_data.json', 'w')

comment_count = 0
post_count = 0

for sub_name in sub_names:
    print(f"Attempting to get top posts and comments from subreddit: {sub_name}")
    sub = reddit.subreddit(sub_name)
    sub_posts = 0
    sub_comments = 0
    for submission in sub.top(limit=None): # will give you ~1000 posts per subreddit
        if not submission.author: # deleted post
            continue
        sub_posts += 1
        print(f"Scraping post: {submission.title}")
        post_title = submission.title.encode('ascii', 'ignore').decode()
        if submission.is_self:
            post_text = submission.selftext.encode('ascii', 'ignore').decode()
            prompt = "<|soss|><|sot|>"
            completion = f"{post_title}<|eot|><|sost|>{post_text}<|eost|><|eoss|><|endoftext|>"
        else:
            prompt = "<|sols|><|sot|>"
            completion = f"{post_title}<|eot|><|sol|>{submission.url}<|eol|><|eols|><|endoftext|>"
        scraped_data.write(json.dumps({'subreddit': sub_name, 'author': submission.author.name, 'id': submission.id, 'content': (prompt+completion), 'score': submission.score}) + '\n')
        submission.comments.replace_more(limit=None)
        comment_list = sorted(submission.comments.list(), key=lambda comment: -comment.score)[:20]
        for comment in comment_list:
            if not comment.author: # deleted comment
                continue
            if comment.score < 5: # low karma comment
                continue
            print(f"Scraping comment: {comment.id}", end='\r', flush=True)
            comment_text = comment.body.encode('ascii', 'ignore').decode()
            if comment.is_submitter:
                completion = f"<|soopr|>{comment_text}<|eoopr|>"
            else:
                completion = f"<|sor|>{comment_text}<|eor|>"
            if comment.submission.is_self:
                completion += "<|eoss|><|endoftext|>"
            else:
                completion += "<|eols|><|endoftext|>"
            sub_comments += 1
            prompt = walk2top(comment)
            scraped_data.write(json.dumps({'subreddit': sub_name, 'author': comment.author.name, 'id': comment.id, 'content': (prompt+completion), 'score': comment.score}) + '\n')
    print(f"Scraped {sub_posts} and {sub_comments} comments from subreddit: {sub_name}")
    comment_count += sub_comments
    post_count += sub_posts

scraped_data.close()
print(f"Scraped {post_count} posts")