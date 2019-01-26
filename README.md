# photos
Simple web app for publishing and displaying photos inspired from
https://github.com/yakamok/simple-gallery

The web app is powered by Flask and a sqlite database 
which acts as a file repository for the photos.

The database (currently) has only one table named *photos*
with an autoincrement column which at the same time acts as
a file name in the file system, the other column holds the 
original file name as it was uploaded and lastly there is
the datetime column which tells the time when the file was 
added to the repository.

In order to reduce their size,the images are resized when 
collected from upload directory through PIL.

In the future, this sql database might be expanded in order to 
include EXIF metadata as well.