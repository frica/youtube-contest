###############################################################################
# Source articles:
#
# Main inspiration:
# http://blog.miguelgrinberg.com/post/easy-web-scraping-with-python
#
# Get video likes-count:
# https://gdata.youtube.com/feeds/api/users/USERNAME_HERE/uploads?v=2&alt=jsonc&max-results=0
# 
# To check manually the count on Youtube: 
# When you open any video it will display the owner's name and the total amount of videos they have to the right
#
# UnicodeError
# http://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
#
###############################################################################

import argparse
import requests
import bs4
import urllib, json
import re
import texttable
from multiprocessing import Pool


def get_videos_urls(author):
	""" return a list of video urls of a given author 
	returns maximum 500 videos for I don't know which reason """
	foundAll = False
	ind = 1
	videos = []
	while not foundAll:
	    inp = urllib.urlopen(r'http://gdata.youtube.com/feeds/api/videos?start-index={0}&max-results=50&alt=json&orderby=published&author={1}'.format( ind, author ) )
	    try:
	        resp = json.load(inp)
	        inp.close()
	        returnedVideos = resp['feed']['entry']
	        for video in returnedVideos:
	            videos.append( video['link'][0]['href'] ) 

	        ind += 50
	        if ( len( returnedVideos ) < 50 ):
	            foundAll = True
	    except:
	        #catch the case where the number of videos in the channel is a multiple of 50
	        print "error"
	        foundAll = True

	return videos


def get_video_data(video_page_url):
	""" returns title, views, likes and dislikes of a given video url """
	video_data = {}
	response = requests.get(video_page_url)
	soup = bs4.BeautifulSoup(response.text)
	video_data['title'] = soup.select('title')[0].get_text()
	
	# careful with the encoding: otherwise it might fail on title like "Dr med Schr(umlaut)fel Interview" 
	#print(u'"{0}"'.format(video_data['title']).encode('ascii', 'ignore'))
	
	# sometimes views are like "42 views" or "2457" with even CR/LF
	try:
		video_data['views'] = int(re.sub('[^0-9]', '',
	                                 soup.select('.watch-view-count')[0].get_text().split()[0]))
	except:
		#print("Error fetching the view count for %s" % video_data['title'].encode('ascii', 'ignore'))
		video_data['views'] = 0

	# sometimes likes / dislikes can be disabled...
	if soup.select('.likes-count'):
		video_data['likes'] = int(re.sub('[^0-9]', '',
	                                 soup.select('.likes-count')[0].get_text().split()[0]))
		video_data['dislikes'] = int(re.sub('[^0-9]', '', 
	                                    soup.select('.dislikes-count')[0].get_text().split()[0]))
	else:
		#print("likes/dislikes not authorized for the video: %s" % video_data['title'].encode('ascii', 'ignore'))
		video_data['likes'] = 0
		video_data['dislikes'] = 0

	return video_data


def parse_args():
	""" parse and return arguments given """
	parser = argparse.ArgumentParser(description='Show video statistics.')
	parser.add_argument('--sort', metavar='FIELD', choices=['views', 'likes', 'dislikes'],
	                    default='views',
	                    help='sort by the specified field. Options are views, likes and dislikes.')
	parser.add_argument('--max', metavar='MAX', type=int, help='show the top MAX entries only.')
	parser.add_argument('--csv', action='store_true', default=False,
	                    help='output the data in CSV format.')
	parser.add_argument('--table', action='store_true', default=False,
	                    help='output the data in an ascii table.')
	parser.add_argument('--workers', type=int, default=8,
	                    help='number of workers to use, 8 by default.')
	return parser.parse_args()


def show_video_stats(author, options):
	""" sort and display a list of max first videos 
	matching the options for a given author """ 
	pool = Pool(options.workers)
	video_page_urls = get_videos_urls(author)
	
	# Warning: pool library is hiding the exception of the methods get_video_data & video_page_urls
	results = sorted(pool.map(get_video_data, video_page_urls), key=lambda video: video[options.sort], reverse=True)
	
	print("Number of videos for %s: %s" % (author, len(results)))

	max = options.max
	if max is None or max > len(results):
	    max = len(results)
	if options.csv:
	    print(u'"title","speakers", "views","likes","dislikes"')
	elif options.table:
		table = texttable.Texttable()
		table.set_cols_align(["c", "r", "r", "r", "l"])
		table.set_cols_width([4, 5, 3, 3, 60])
		table.header(["Rank", "Views", "+1", "-1", "Title"])
	else:
	    print(u'Rank  Views  +1  -1 Title')

	for i in range(max):
		if options.csv:
			print(u'"{0}","{1}",{2},{3}'.format(
				results[i]['title'], results[i]['views'],
				results[i]['likes'], results[i]['dislikes']))
		elif options.table:
			table.add_row([i+1, results[i]['views'], results[i]['likes'], 
				results[i]['dislikes'],
				results[i]['title'].encode('ascii', 'ignore')])
		else:
			print(u'{0:2d} {1:5d} {2:3d} {3:3d} {4}'.format(i+1,
	            results[i]['views'], results[i]['likes'], 
	            results[i]['dislikes'], results[i]['title']))

	if options.table:
		print "\n" + table.draw() + "\n"


if __name__ == '__main__':
	# Example: python contest.py --sort views --max 10 --table --worker 8	
	authors = ('agfahealthcarevideo', 'gehealthcare', 'PhilipsHC')
	for author in authors:
		print author
		show_video_stats(author, parse_args())
