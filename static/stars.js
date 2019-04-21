document.addEventListener('DOMContentLoaded', function() {

    var ratingnum = document.querySelectorAll('span.rating');

    for (var i = 0, len = ratingnum.length; i<len; i++){
        
        if (ratingnum[i].innerHTML === '5') {
            ratingnum[i].innerHTML = `<span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>`;
        }
        else if (ratingnum[i].innerHTML === '4') {
            ratingnum[i].innerHTML = `<span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>`;
        }
        else if (ratingnum[i].innerHTML === '3') {
            ratingnum[i].innerHTML = `<span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>`;
        } 
        else if (ratingnum[i].innerHTML === '2') {
            ratingnum[i].innerHTML = `<span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>
                                    <span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>`;
        }
        else if (ratingnum[i].innerHTML === '1') {
            ratingnum[i].innerHTML = '<span style="font-size: 1em; color: Gold;"><i class="fas fa-star"></i></span>';
        } 
    }
})