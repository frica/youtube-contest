youtube-contest
===============

Compares the popularity of several YouTube channels


Most of the code is shamelessly borrowed from a nice article from Miguel Grinberg: http://blog.miguelgrinberg.com/post/easy-web-scraping-with-python.
I adapted the code to be able to compare the popularity of the videos from several channels. 
My goal was to compare the popularity of the main actors of Healthcare industry on YouTube.


Improvements to the original script:
- added a method to get all videos URLs from a channel
- added a check for videos forbidding likes/dislikes
- added a check for videos with title using non ascii characters
- added a formatting in ascii table with texttable (http://foutaise.org/code/texttable/)
