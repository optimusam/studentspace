$(document).ready(function() {

    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
  
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

        
    });
    let teacher_id = location.pathname.split('/')[2]
    let course = $('.user-review-course').text().replace('Course: ', '')
    let stars = $('.user-review-rating').text()
    let review = $('.user-review').text()
    let isAnon = $('#anon').is(':checked')
    $(".edit").click(function() {
        $.when(function() {
            $(".user-review-box").html(`
            <form action="/teacher/${teacher_id}/review" method="post" class="review">
            <div class="field">
              <select id="rating" required name="rating">
                <option disabled selected value>0</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
              </select>
            </div>
            <div class="field">
              <label class="label">Course Code/Name</label>
              <div class="control">
                <input type="text" required class="input" name="course" value="${course}" placeholder="The Course taught by the teacher">
              </div>
            </div>
            <div class="field">
              <label class="label">Review</label>
              <div class="control">
                <textarea class="textarea is-primary" required name="review" placeholder="Your Review">${review}</textarea>
              </div>
            </div>
            <div class="field">
              <div class="control">
                <label class="checkbox">
                  <input type="checkbox" name="anon" id="anon">
                  I want to review anonymously
                </label>
              </div>
            </div>
            <div class="field">
              <div class="control">
                  <button type="submit" class="button is-info">Submit</button>
              </div>
            </div>
        </form>`)
        }()).then(makeStars(isAnon))
        });
        
    });
function makeStars(isAnon) {
    $('#rating').barrating({
        theme: 'fontawesome-stars'
    })
    console.log(isAnon)
    $('#anon').attr('checked', isAnon)
}

