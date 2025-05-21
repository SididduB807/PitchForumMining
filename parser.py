__author__ = 'DarkWeb'

import os
from bs4 import BeautifulSoup
from datetime import datetime
from Forums.Utilities.utilities import cleanString

# Description page parser for Pitch
def pitch_description_parser(soup):
    topic_tag = soup.find('h1', class_='p-title-value')
    topic = cleanString(topic_tag.text) if topic_tag else '-1'

    user = []
    status = []
    post = []
    addDate = []
    sign = []
    image_user = []
    image_post = []

    posts = soup.find_all('article', class_='message')

    for p in posts:
        author_tag = p.find('a', class_='username')
        user.append(cleanString(author_tag.text) if author_tag else 'Unknown')

        title_tag = p.find('h5', class_='userTitle')
        status.append(cleanString(title_tag.text) if title_tag else '-1')

        content_tag = p.find('div', class_='message-body')
        post.append(cleanString(content_tag.text) if content_tag else 'No content')

        time_tag = p.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            try:
                dt = datetime.fromisoformat(time_tag['datetime'].replace('Z', ''))
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()
        addDate.append(dt)

        sig_tag = p.find('div', class_='signature')
        sign.append(cleanString(sig_tag.text) if sig_tag else '-1')

        avatar_tag = p.find('img', class_='avatar')
        if avatar_tag and avatar_tag.has_attr('src'):
            image_user.append(avatar_tag['src'].split('base64,')[-1])
        else:
            image_user.append('-1')

        first_img = content_tag.find('img') if content_tag else None
        if first_img and first_img.has_attr('src'):
            image_post.append(first_img['src'].split('base64,')[-1])
        else:
            image_post.append('-1')

    return (topic, user, status, ['-1'] * len(user), ['-1'] * len(user), sign, post, ['-1'] * len(user), addDate, image_user, image_post)


# Listing page parser for Pitch
def pitch_listing_parser(soup):
    forum = "Pitch"
    board = "Hacking"
    author = []
    topic = []
    views = []
    posts = []
    href = []
    addDate = []
    image_author = []

    threads = soup.find_all('div', class_='structItem--thread')

    for thread in threads:
        title_tag = thread.find('a', class_='structItem-title')
        topic.append(cleanString(title_tag.text) if title_tag else '-1')
        href.append(title_tag['href'] if title_tag and title_tag.has_attr('href') else '-1')

        user_tag = thread.find('a', class_='username')
        author.append(cleanString(user_tag.text) if user_tag else 'Unknown')

        reply_tag = thread.find('dl', class_='pairs pairs--justified')
        posts.append(reply_tag.find('dd').text.strip() if reply_tag else '-1')

        view_tag = thread.find('dl', class_='pairs pairs--justified', string="Views")
        views.append(view_tag.find('dd').text.strip() if view_tag else '-1')

        time_tag = thread.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            try:
                dt = datetime.fromisoformat(time_tag['datetime'].replace('Z', ''))
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()
        addDate.append(dt)

        image_author.append('-1')

    return (forum, len(topic), board, author, topic, views, posts, href, addDate, image_author)


# Extract description page links from listing page
def pitch_links_parser(soup):
    links = []
    anchors = soup.find_all('a', href=True)
    for a in anchors:
        href = a['href']
        if '/threads/' in href:
            links.append(href)
    return links[:1]  # Only one link for testing
