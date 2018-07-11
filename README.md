## The Problem: Image gallery

You got a request from a friend to create a gallery for his weeding where his friends will be able to upload their photos and he`ll have a unified gallery with all friend's photos.
He wants to be able to approve the the photos before be visible to everyone. He and his wife should be the only one able to approve new photos.
Users must be able to like photos and photos with more likes should be listed first in the page.

Please create a website that supply their needs. The photos must be saved on Amazon AWS S3 and the gallery must be fast to open even if there many photos.


Details of the solution
- The resolution must be a web application.
- There must supply all the information needed to test the application
- The application must run
- The code needs to be hosted in your preferred code repository
- You need to host the application in a server of your choice and give us a link to access and use the application
- You should provide sufficient evidence that your solution is complete by, as a minimum, indicating that it works correctly against the requirements


## Possible improvements
1. Implement tests
2. Add pagination to the gallery views
3. Add design (instead of just plain bootstrap in a hurry)
4. The design of the image uploader could be better.
5. Add "zoom" to the images on click (a modal facebook like or a page only for them)
6. Improve the approve link error handling.
7. Add cache to views/calls around.
8. Add a crud page to manage users.
9. Improve the like/dislike performance.
10. Delete the photos on s3 as their references are deleted on the database.