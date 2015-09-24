for (var i = 1; i < 38; i++) {
    var myArray = [1, 3, 4, 5, 6, 8 , 13, 14, 15, 17, 18, 19, 23, 24, 26, 29, 30, 31, 33, 34, 35];
    //if(i =! 1 && i != 7 && i){
    if($.inArray(i,myArray) != -1){
        document.write('<a class="example-image-link" href="img/photo_page/images/' + i + '.jpg" ' +
        'data-lightbox="example-set"><img width="240" height="180" class="example-image" src="img/photo_page/thumbnails/' + i + '.jpg" alt=""/></a>');
    }
};