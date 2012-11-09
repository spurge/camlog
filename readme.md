camlog
======

_This is only a draft at the moment_

camlog logs what you're doing through your webcam and a screenshot. Use
it with cron and merge the results into a movie or just as a log of what
you're up to.

Or use it to capture the thief that robbed your laptop.

There will be support for automatic posting to a specified blog or
uploading to some defined host.

How does it work at the moment?
-------------------------------

* It's a python script.
* It uses *opencv* and *gtk*, witch you'll have to install.
* It captures a frame with your webcam (if you have one).
* And it takes a screenshot.
* Then it fetches your external ip-address, hostname, isp, country,
  city, latitude and longitude.
* The two image-files and your network identity will then get
  compressed with tar and gzip and named with year, month, day,
  hour and second.
